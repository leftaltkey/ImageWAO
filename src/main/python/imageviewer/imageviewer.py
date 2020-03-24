
from PySide2 import QtCore, QtGui, QtWidgets


class QImageViewer(QtWidgets.QGraphicsView):

    def __init__(self):
        super().__init__()

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.setScene(QtWidgets.QGraphicsScene())

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = QtCore.Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

    @property
    def viewBoundingBox(self):
        '''
        Bounding box of the current view.
        '''
        A = self.mapToScene(QtCore.QPoint(0, 0)) 
        B = self.mapToScene(QtCore.QPoint(
            self.viewport().width(), 
            self.viewport().height()))
        viewBBox = QtCore.QRectF(A, B)

        # This box might include parts of the scene outside
        # the rect -- this is invalid. Need to intersect with
        # the scene rect.
        return viewBBox.intersected(self.sceneRect())

    def hasImage(self):
        '''
        Returns whether or not the scene contains an image pixmap.
        '''
        return self._pixmapHandle is not None

    def clearImage(self):
        '''
        Removes the current image pixmap from the scene if it exists.
        '''
        if self.hasImage():
            self.scene().removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        '''
        Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        '''
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        '''
        Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        '''
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def scenePixmap(self):
        return self._pixmapHandle

    @QtCore.Slot(QtGui.QImage)
    def setImage(self, image):
        '''
        Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        '''
        if type(image) is QtGui.QPixmap:
            pixmap = image
        elif type(image) is QtGui.QImage:
            pixmap = QtGui.QPixmap.fromImage(image)
        else:
            raise RuntimeError('ImageViewer.setImage: Argument must be a QImage or QPixmap.')
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene().addPixmap(pixmap)
        self.setSceneRect(QtCore.QRectF(pixmap.rect()))  # Set scene size to image size.
        if self.canZoom:
            self.zoomStack = []  # Clear zoom stack.
        self.updateViewer()

    def updateViewer(self):
        '''
        Show current zoom (if showing entire image, apply current aspect ratio mode).
        '''
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], QtCore.Qt.KeepAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        '''
        Maintain current zoom on resize.
        '''
        self.updateViewer()

    def clearZoom(self):
        '''
        Clears and resets the zoom stack
        '''
        self.zoomStack = []
        self.updateViewer()

    def zoomIn(self, percent):
        '''
        Zooms the view in by a given percent.
        Percentage on scale of 0 to 1.
        '''
        viewBBox = self.viewBoundingBox
        margin = int(viewBBox.width() * percent)
        smallerRect = viewBBox.marginsRemoved(QtCore.QMargins(margin, margin, margin, margin))
        self.zoomTo(smallerRect)

    def zoomTo(self, rect):
        '''
        Zoom the view to the given rectangle.
        This is most commonly used with rubberband
        selection rectangles
        '''
        
        viewBBox = self.viewBoundingBox
        
        # The box that we want to zoom to is the one that
        # intersects with the view's bounding box.
        # (E.g. if the requested box is outside the scene,
        # clip the box to the scene's limits)
        selectionBBox = rect.intersected(viewBBox)

        # Clear current selection area.
        self.scene().setSelectionArea(QtGui.QPainterPath())

        # Execute zoom
        if selectionBBox.isValid() and (selectionBBox != viewBBox):
            self.zoomStack.append(selectionBBox)
            self.updateViewer()

    def zoomOutOneLevel(self):
        '''
        Zooms the view by a single zoom level.
        '''
        if len(self.zoomStack):
            self.zoomStack.pop()
            self.updateViewer()

