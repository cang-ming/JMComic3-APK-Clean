"""Run with: python scripts/test_mod_apk.py (requires Node.js)."""
import contextlib
import io
from pathlib import Path
import tempfile

from mod_apk import apply_patches, validate_javascript


with tempfile.TemporaryDirectory() as root:
    js = Path(root) / "assets/public/static/js"
    js.mkdir(parents=True)
    links = js / "6811.fixture.chunk.js"
    links.write_text(
        "function links(n,r){return[...n.first_links||[],...r]}"
        "function untouched(){return[1,2]}", encoding="utf-8")
    popup = js / "5840.fixture.chunk.js"
    popup.write_text(
        'function popup(L){var e;const t=null===L||void 0===L||'
        'null===(e=L.pop1_list)||void 0===e?void 0:e.advs;'
        'return(null===t||void 0===t?void 0:t.length)>1?'
        'choose(t):{items:t||[]}};const G=e=>{const{onNext:t}=e,'
        'i=timer(3000);return render(i)},V=e=>confirmAge(e);'
        'const Oe=!Ie&&(cover.length>0);', encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        apply_patches(root)
    assert links.read_text(encoding="utf-8") == (
        "function links(n,r){return[]}function untouched(){return[1,2]}")
    assert "const t=[];return" in popup.read_text(encoding="utf-8")
    assert 'return null},V=e=>confirmAge(e)' in popup.read_text(encoding="utf-8")
    assert '(0,a.useEffect)((()=>{t()}),[t])' in popup.read_text(encoding="utf-8")
    validate_javascript(root)
    links.write_text("function broken(){return[],...r]}", encoding="utf-8")
    try:
        validate_javascript(root)
    except RuntimeError as error:
        assert "6811.fixture.chunk.js" in str(error)
    else:
        raise AssertionError("Broken JavaScript was accepted")
print("Patch regressions and invalid-JavaScript rejection passed.")
