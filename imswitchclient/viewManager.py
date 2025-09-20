class viewManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def setLiveViewActive(self, active):
        """Enable or disable live view"""
        url = f"{self.parent.base_uri}/ViewController/setLiveViewActive"
        payload = {
            'active': active
        }
        response = self.parent.get_json(url, payload=payload)
        return response
    
    def setLiveViewCrosshairVisible(self, visible):
        """Show or hide crosshair in live view"""
        url = f"{self.parent.base_uri}/ViewController/setLiveViewCrosshairVisible"
        payload = {
            'visible': visible
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setLiveViewGridVisible(self, visible):
        """Show or hide grid in live view"""
        url = f"{self.parent.base_uri}/ViewController/setLiveViewGridVisible"
        payload = {
            'visible': visible
        }
        response = self.parent.get_json(url, payload=payload)
        return response