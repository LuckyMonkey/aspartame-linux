from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_gtk4_home_search_initializes_lazy_list_before_filtering():
    source = (ROOT / "patches/gtk4-preview/0012-home-lazy-list-search.patch").read_text()
    assert "if self._list_view is None:" in source
    assert "self._list_view = ActivitiesList()" in source
    assert "self._list_view.set_filter(self._query)" in source


def test_gtk4_home_search_patch_is_ordered_after_home_startup_patches():
    patches = sorted((ROOT / "patches/gtk4-preview").glob("00*.patch"))
    assert patches[-1].name == "0012-home-lazy-list-search.patch"
