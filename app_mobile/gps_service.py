try:
    from plyer import gps
except Exception:
    gps = None


class GPSService:
    def __init__(self):
        self.latitude = ""
        self.longitude = ""
        self.ativo = False

    def _on_location(self, **kwargs):
        lat = kwargs.get("lat")
        lon = kwargs.get("lon")

        if lat is not None:
            self.latitude = str(lat)
        if lon is not None:
            self.longitude = str(lon)

    def _on_status(self, stype, status):
        pass

    def iniciar(self):
        if gps is None:
            return False

        try:
            gps.configure(on_location=self._on_location, on_status=self._on_status)
            gps.start(minTime=1000, minDistance=1)
            self.ativo = True
            return True
        except Exception:
            return False

    def parar(self):
        if gps and self.ativo:
            try:
                gps.stop()
            except Exception:
                pass
            self.ativo = False