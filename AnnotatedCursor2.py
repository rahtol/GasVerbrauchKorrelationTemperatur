import matplotlib.pyplot as plt
import numpy as np
import logging
from matplotlib.backend_bases import MouseEvent
from matplotlib.widgets import Cursor


class AnnotatedCursor2(Cursor):
    """
    A crosshair cursor like `~matplotlib.widgets.Cursor` with a text showing \
    the current coordinates.

    For the cursor to remain responsive you must keep a reference to it.
    The data of the axis specified as *dataaxis* must be in ascending
    order. Otherwise, the `numpy.searchsorted` call might fail and the text
    disappears. You can satisfy the requirement by sorting the data you plot.
    Usually the data is already sorted (if it was created e.g. using
    `numpy.linspace`), but e.g. scatter plots might cause this problem.
    The cursor sticks to the plotted line.

    Parameters
    ----------
    data : array dictionary defining the scatter plot, see extend_xls_by_temperature2.py
      

    numberformat : `python format string <https://docs.python.org/3/\
    library/string.html#formatstrings>`_, optional, default: "{0:.4g};{1:.4g}"
        The displayed text is created by calling *format()* on this string
        with the two coordinates.

    offset : (float, float) default: (5, 5)
        The offset in display (pixel) coordinates of the text position
        relative to the cross-hair.

    dataaxis : {"x", "y"}, optional, default: "x"
        If "x" is specified, the vertical cursor line sticks to the mouse
        pointer. The horizontal cursor line sticks to *line*
        at that x value. The text shows the data coordinates of *line*
        at the pointed x value. If you specify "y", it works in the opposite
        manner. But: For the "y" value, where the mouse points to, there might
        be multiple matching x values, if the plotted function is not biunique.
        Cursor and text coordinate will always refer to only one x value.
        So if you use the parameter value "y", ensure that your function is
        biunique.

    Other Parameters
    ----------------
    textprops : `matplotlib.text` properties as dictionary
        Specifies the appearance of the rendered text object.

    **cursorargs : `matplotlib.widgets.Cursor` properties
        Arguments passed to the internal `~matplotlib.widgets.Cursor` instance.
        The `matplotlib.axes.Axes` argument is mandatory! The parameter
        *useblit* can be set to *True* in order to achieve faster rendering.

    """

    def __init__(self, data, linear_regression, offset=(5, 5), textprops=None, **cursorargs):
        if textprops is None:
            textprops = {}
        # The line object, for which the coordinates are displayed
        self.data = data
        # The format string, on which .format() is called for creating the text
        self.linear_regression = linear_regression
        # Text position offset
        self.offset = np.array(offset)

        # First call baseclass constructor.
        # Draws cursor and remembers background for blitting.
        # Saves ax as class attribute.
        super().__init__(**cursorargs)

        # Default value for position of text.
        self.set_position(self.data.iloc[0]['temperatur'], self.data.iloc[0]['energy_per_day'],0,0)
        # Create invisible animated text
        self.text = self.ax.text(
            self.ax.get_xbound()[0],
            self.ax.get_ybound()[0],
            "0, 0",
            animated=bool(self.useblit),
            visible=False, **textprops)
        # The position at which the cursor was last drawn
        self.lastdrawnplotpoint = None

    def onmove(self, event):
        """
        Overridden draw callback for cursor. Called when moving the mouse.
        """

        # Leave method under the same conditions as in overridden method
        if self.ignore(event):
            self.lastdrawnplotpoint = None
            return
        if not self.canvas.widgetlock.available(self):
            self.lastdrawnplotpoint = None
            return

        # If the mouse left drawable area, we now make the text invisible.
        # Baseclass will redraw complete canvas after, which makes both text
        # and cursor disappear.
        if event.inaxes != self.ax:
            self.lastdrawnplotpoint = None
            self.text.set_visible(False)
            super().onmove(event)
            return

        # Get the coordinates, which should be displayed as text,
        # if the event coordinates are valid.
        plotpoint = None
        if event.xdata is not None and event.ydata is not None:
            # Get plot point related to current x position.
            # These coordinates are displayed in text.
            plotpoint = self.set_position(event.xdata, event.ydata, event.x, event.y)
            # Modify event, such that the cursor is displayed on the
            # plotted line, not at the mouse pointer,
            # if the returned plot point is valid
            if plotpoint is not None:
                event.xdata = plotpoint[0]
                event.ydata = plotpoint[1]

        # If the plotpoint is given, compare to last drawn plotpoint and
        # return if they are the same.
        # Skip even the call of the base class, because this would restore the
        # background, draw the cursor lines and would leave us the job to
        # re-draw the text.
        if plotpoint is not None and plotpoint == self.lastdrawnplotpoint:
            return

        # Remember the recently drawn cursor position, so events for the
        # same position (mouse moves slightly between two plot points)
        # can be skipped
        self.lastdrawnplotpoint = plotpoint

        # Baseclass redraws canvas and cursor. Due to blitting,
        # the added text is removed in this call, because the
        # background is redrawn.
        super().onmove(event)

        # Check if the display of text is still necessary.
        # If not, just return.
        # This behaviour is also cloned from the base class.
        if not self.get_active() or not self.visible:
            return

        # Draw the widget, if event coordinates are valid.
        if plotpoint is not None:
            # Update position and displayed text.
            # Position: Where the event occurred.
            # Text: Determined by set_position() method earlier
            # Position is transformed to pixel coordinates,
            # an offset is added there and this is transformed back.
            y_regression = self.linear_regression['a'] * event.xdata + self.linear_regression['b']
            if event.ydata > y_regression:
                self.text.set_horizontalalignment('left')
                self.text.set_verticalalignment('bottom')
                self.offset = np.absolute(self.offset)
            else:
                self.text.set_horizontalalignment('right')
                self.text.set_verticalalignment('top')
                self.offset = np.absolute(self.offset) * -1

            temp = [event.xdata, event.ydata]
            temp = self.ax.transData.transform(temp)
            temp = temp + self.offset
            temp = self.ax.transData.inverted().transform(temp)
            self.text.set_position(temp)
            t0 = plotpoint[2]
            t1 = plotpoint[3]
            dateformat = '%d.%m.%Y %H:%M'
            self.text.set_text(t0.strftime(dateformat) + '\n' + t1.strftime(dateformat))
            self.text.set_visible(self.visible)
            reposition_text = False

            x_limits = self.ax.xaxis.get_view_interval()
            y_limits = self.ax.yaxis.get_view_interval()
            renderer = self.ax.figure.canvas.get_renderer()
            t_bbox = self.text.get_window_extent(renderer)
            (x0, y0) = self.ax.transData.inverted().transform((t_bbox.x0, t_bbox.y0))
            (x1, y1) = self.ax.transData.inverted().transform((t_bbox.x1, t_bbox.y1))
            if x0 < x_limits[0]:
                self.text.set_horizontalalignment('left')
                self.offset[0] = -self.offset[0]
                reposition_text = True
            if x1 > x_limits[1]:
                self.text.set_horizontalalignment('right')
                self.offset[0] = -self.offset[0]
                reposition_text = True
            if y0 < y_limits[0]:
                self.text.set_verticalalignment('bottom')
                self.offset[1] = -self.offset[1]
                reposition_text = True
            if y1 > y_limits[1]:
                self.text.set_verticalalignment('top')
                self.offset[1] = -self.offset[1]
                reposition_text = True
            if reposition_text: 
                temp = [event.xdata, event.ydata]
                temp = self.ax.transData.transform(temp)
                temp = temp + self.offset
                temp = self.ax.transData.inverted().transform(temp)
                self.text.set_position(temp)

            #print(f'x_limits={x_limits}, y_limits={y_limits}, t_x0y0={(x0,y0)}, t_x1y1={(x1,y1)} t_bbox={t_bbox}')

            # Tell base class, that we have drawn something.
            # Baseclass needs to know, that it needs to restore a clean
            # background, if the cursor leaves our figure context.
            self.needclear = True

        # otherwise, make text invisible
        else:
            self.text.set_visible(False)

        # Draw changes. Cannot use _update method of baseclass,
        # because it would first restore the background, which
        # is done already and is not necessary.
        if self.useblit:
            self.ax.draw_artist(self.text)
            self.canvas.blit(self.ax.bbox)
        else:
            # If blitting is deactivated, the overridden _update call made
            # by the base class immediately returned.
            # We still have to draw the changes.
            self.canvas.draw_idle()

    def set_position(self, xpos, ypos, x, y):
        """
        Finds the coordinates, which have to be shown in text.

        Function looks up the matching scatter plot point for the given mouse position.

        Parameters
        ----------
        xpos : float
            The current x position of the cursor in data coordinates.
            Important if *dataaxis* is set to 'x'.
        ypos : float
            The current y position of the cursor in data coordinates.
            Important if *dataaxis* is set to 'y'.

        Returns
        -------
        ret : {2D array-like, None}
            The coordinates which should be displayed.
            *None* is the fallback value.
        """

        ret_coords = None # default return value is None if no point is close enough to the cursor coordinates
        i_min: int = -1
        min_dist: float = 999999.0
        for i in range(len(self.data)):
            xdata = self.data.iloc[i]['temperatur']
            ydata = self.data.iloc[i]['energy_per_day']
            # transform to pixel coordinates since this is the only coordinate system to measure meaningful distances
            xi, yi = self.ax.transData.transform([xdata, ydata])
            # squared euclidean distance in 2D
            dist: float = (x - xi) **2 + (y - yi) **2
            if dist < min_dist:
                min_dist = dist
                i_min = i
        if min_dist < 10.0:
            ret_coords = [self.data.iloc[i_min]['temperatur'], 
                          self.data.iloc[i_min]['energy_per_day'], 
                          self.data.iloc[i_min]['t0'],
                          self.data.iloc[i_min]['t1']]
#        print(f'min_dist={min_dist}, ret_coords={ret_coords}')

        return ret_coords

    def clear(self, event):
        """
        Overridden clear callback for cursor, called before drawing the figure.
        """

        # The base class saves the clean background for blitting.
        # Text and cursor are invisible,
        # until the first mouse move event occurs.
        super().clear(event)
        if self.ignore(event):
            return
        self.text.set_visible(False)

    def _update(self):
        """
        Overridden method for either blitting or drawing the widget canvas.

        Passes call to base class if blitting is activated, only.
        In other cases, one draw_idle call is enough, which is placed
        explicitly in this class (see *onmove()*).
        In that case, `~matplotlib.widgets.Cursor` is not supposed to draw
        something using this method.
        """

        if self.useblit:
            super()._update()
