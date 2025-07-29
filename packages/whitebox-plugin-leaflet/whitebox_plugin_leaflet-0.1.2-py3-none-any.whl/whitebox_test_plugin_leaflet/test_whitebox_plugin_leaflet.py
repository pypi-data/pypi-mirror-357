from django.test import TestCase

from plugin.manager import plugin_manager


class TestWhiteboxPluginLeaflet(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.plugins
                if x.__class__.__name__ == "WhiteboxPluginLeaflet"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "Leaflet provider")

    def test_get_bootstrap_assets(self):
        expected = {
            "js": [
                "/static/whitebox_plugin_leaflet/leaflet/leaflet.js",
                "/static/whitebox_plugin_leaflet/leaflet-rotatedMarker/leaflet.rotatedMarker.js",
            ],
            "css": [
                "/static/whitebox_plugin_leaflet/leaflet/leaflet.css",
            ],
        }
        self.assertEqual(self.plugin.get_bootstrap_assets(), expected)
