from kivy.clock import Clock

try:
    from plyer import gps
except Exception:
    gps = None


class GPSService:
    def __init__(self):
        self.last_lat = ""
        self.last_lon = ""
        self.callback = None
        self.started = False

    def configure(self, callback):
        self.callback = callback

    def _on_location(self, **kwargs):
        self.last_lat = str(kwargs.get("lat", ""))
        self.last_lon = str(kwargs.get("lon", ""))
        if self.callback:
            self.callback(self.last_lat, self.last_lon)

    def _on_status(self, stype, status):
        pass

    def start(self):
        if not gps:
            return False, "GPS não disponível neste ambiente."
        try:
            gps.configure(on_location=self._on_location, on_status=self._on_status)
            gps.start(minTime=1000, minDistance=1)
            self.started = True
            return True, "GPS iniciado."
        except Exception as e:
            return False, f"Erro ao iniciar GPS: {e}"

    def stop(self):
        if gps and self.started:
            try:
                gps.stop()
            except Exception:
                pass
        self.started = False

    def mock_fill_desktop(self):
        def fill(_dt):
            if self.callback:
                self.callback("-3.7318621", "-38.5266704")
        Clock.schedule_once(fill, 1)