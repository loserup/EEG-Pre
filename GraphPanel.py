import wx


class graphPanel(wx.Panel):

    def __init__(self, parent, eeg, w, h):
        wx.Panel.__init__(self, parent, size=(w, h),
                          style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.paint = True
        self.eeg = eeg
        self.timeLapse = 0
        self.incx = 1
        self.w = self.Size[0]
        # list of channels in screen and start position
        self.chanPosition = []
        # vars for zooming
        self.zoom = False
        self.strCh = 0
        self.endCh = len(eeg.channels)
        self.totalChan = len(eeg.channels) + len(eeg.additionalData)
        self.strMs = 0
        self.zoomPile = []
        # var for moving graph
        self.move = False
        self.strMove = None
        self.endMove = None
        self.nSamp = self.eeg.frequency * self.eeg.duration
        self.msShowing = self.eeg.duration * 1000
        self.setSamplingRate()
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClickDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickReleased)
        self.Bind(wx.EVT_MOTION, self.MovingMouse)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnClickDown(self, event):
        if self.move:
            self.strMove = event.GetPosition()
        else:
            self.GetParent().zoomP.OnClickDown(event.GetPosition())

    def MovingMouse(self, event):
        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = self.endMove
        else:
            self.GetParent().zoomP.MovingMouse(event.GetPosition())

    def OnClickReleased(self, event):

        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = None
                self.endMove = None
        else:
            self.GetParent().zoomP.OnClickReleased(event.GetPosition())

    # moves the eeg when it is zoomed
    def moveGraph(self):
        if self.zoom:
            pos = self.chanPosition
            start = self.strMove
            end = self.endMove

            if len(pos) < 2:
                chanH = self.Size[1]
            else:
                c = pos[0]
                cx = pos[1]
                chanH = cx[1] - c[1]
            height = abs(end[1] - start[1])
            chansMoved = int(height / chanH)
            chansShowing = self.endCh - self.strCh

            if end[1] < start[1]:
                self.strCh += chansMoved
            else:
                self.strCh -= chansMoved
            self.endCh = self.strCh + chansShowing
            # making sure it is a valid index
            if self.strCh < 0 or self.endCh < 0:
                self.strCh = 0
                self.endCh = chansShowing
            if self.strCh > len(self.eeg.channels) - 1 or self.endCh > self.totalChan - 1:
                self.strCh = self.totalChan - chansShowing
                self.endCh = self.totalChan

            length = abs(end[0] - start[0])

            # getting the readings to show
            endMs = self.strMs + self.msShowing
            if end[0] < start[0]:
                self.strMs += (length * self.timeLapse) / self.incx
                # make sure it is not longer than the actual readings
                if (self.strMs + endMs) > self.eeg.duration * 1000:
                    self.strMs = (self.eeg.duration * 1000) - self.msShowing
            else:
                self.strMs -= (length * self.timeLapse) / self.incx
                # make sure it does not go to negative index
                if self.strMs < 0:
                    self.strMs = 0

            # repainting
            self.paint = True
            self.GetParent().Refresh()
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].moveZom(self.strMs, self.endRead)
            chil[4].zoomManager(len(ch))
            chil[5].adjustment(ch)
            self.strMove = self.endMove

    def setSamplingRate(self):
        if self.msShowing < self.w:
            self.incx = self.w / self.msShowing
            self.timeLapse = 1
        else:
            self.incx = 1
            self.timeLapse = self.msShowing / self.w

    # gets the selected electrodes to graph
    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.eeg.channels):
                channels.append(self.eeg.channels[ix])
            else:
                channels.append(self.eeg.additionalData[ix - len(self.eeg.channels)])
        return channels

    # changes the value for printable purposes
    def ChangeRange(self, v, nu, nl):
        oldRange = self.eeg.amUnits[0] - self.eeg.amUnits[1]
        newRange = nu - nl
        newV = round((((v - self.eeg.amUnits[1]) * newRange) / oldRange) + nl, 2)
        return newV

    def resetZoom(self):
        self.zoom = False
        self.strMs = 0
        self.strCh = 0
        self.endCh = len(self.getChecked())
        self.msShowing = self.eeg.duration * 1000
        self.setSamplingRate()
        self.zoomPile = []
        # repainting
        self.paint = True
        self.GetParent().Refresh()

    def apply(self):
        # repainting
        self.paint = True
        self.GetParent().Refresh()

    def returnZoom(self):
        if len(self.zoomPile) > 0:
            zoom = self.zoomPile.pop(len(self.zoomPile) - 1)
            self.strMs = zoom[0]
            self.timeLapse = zoom[1]
            self.incx = zoom[2]
            self.strCh = zoom[3]
            self.endCh = zoom[4]
            self.msShowing = zoom[5]
            # repainting
            self.paint = True
            self.GetParent().Refresh()
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].zoomOut()
            chil[4].zoomManager(len(ch))
            chil[5].adjustment(ch)
        else:
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].update()
            chil[4].zoomManager(len(ch))
            chil[5].adjustment()
            self.resetZoom()

    def setZoom(self, start, end):
        # adding this zoom to the pile
        self.zoomPile.append([self.strMs, self.timeLapse, self.incx, self.strCh, self.endCh, self.msShowing])
        self.zoom = True
        tmpS = self.strCh

        i = 0
        pos = self.chanPosition
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i + 1]
            if c[1] <= start[1] <= cx[1]:
                break
            i += 1
        self.strCh = i
        i = 0
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i + 1]
            if c[1] <= end[1] <= cx[1]:
                break
            i += 1
        self.endCh = i + 1
        if self.endCh <= self.strCh:
            self.endCh = self.strCh + 1
        tmpE = self.endCh - self.strCh
        self.strCh += tmpS
        self.endCh = self.strCh + tmpE
        # getting the readings to show
        startr = self.strMs
        self.strMs += (start[0] * self.timeLapse) / self.incx
        endMs = startr + (end[0] * self.timeLapse) / self.incx
        self.msShowing = endMs - self.strMs
        if self.msShowing < 10:
            self.msShowing = 10
        if self.strMs + self.msShowing > self.eeg.duration * 1000:
            self.strMs = (self.eeg.duration * 1000) - self.msShowing
        self.setSamplingRate()
        # repainting
        self.paint = True
        self.GetParent().Refresh()
        # changing channel labels
        chil = self.GetParent().GetChildren()
        ch = self.getViewChannels()
        chil[4].zoomManager(len(ch))
        chil[5].adjustment(ch)

    def getViewChannels(self):
        checked = self.getChecked()
        channels = []
        # if there is zoom
        if self.zoom:
            i = self.strCh
            r = self.endCh - i
            if self.endCh > len(checked):
                i -= (self.endCh - len(checked))
                self.endCh = len(checked)
            if r > len(checked):
                self.endCh = len(checked)
            if i < 0:
                i = 0
            self.strCh = i
            while i < self.endCh:
                channels.append(checked[i])
                i += 1
        else:
            channels = checked
        return channels

    def msToReading(self, ms):
        return int((ms * self.nSamp) / (self.eeg.duration * 1000))

    def OnPaint(self, event=None):
        # buffered so it doesn't paint channel per channel
        if self.paint:
            dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
            dc.Clear()
            dc.SetPen(wx.Pen(wx.BLACK, 4))
            y = 0

            amUnits = self.eeg.amUnits
            timeLapse = self.timeLapse
            incx = self.incx
            self.chanPosition = []
            # defining channels to plot
            channels = self.getViewChannels()
            if len(channels) > 0:
                hSpace = (self.Size[1] - 5) / len(channels)
                w = self.w
                dc.SetPen(wx.Pen(wx.BLACK, 1))
                for channel in channels:
                    x = 0
                    ms = self.strMs
                    i = self.msToReading(ms)
                    self.chanPosition.append([channel.label, y])
                    while i < self.nSamp:
                        inci = self.msToReading(ms + timeLapse)
                        ny = (((channel.readings[i] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                        if inci > self.nSamp - 1:
                            ny2 = ny
                        else:
                            ny2 = (((channel.readings[inci] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                        if abs(ny - ny2) > 3 or (x + incx) > 3:
                            dc.DrawLine(x, ny, x + incx, ny2)
                        else:
                            dc.DrawPoint(x, ny)
                        ms += timeLapse
                        i = self.msToReading(ms)
                        x += incx
                    y += hSpace
            self.paint = False