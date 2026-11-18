"""Selective extraction regressions reused from PR #67 ed0250b/test_local.py."""
import hashlib,io,json,pathlib,tarfile,tempfile,time,unittest
from unittest.mock import patch
import materialize

class ExtractionTests(unittest.TestCase):
    """Synthetic OCI archives exercise the real blob verifier and selective extractor."""
    def fixture(self, root, members):
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w') as archive:
            for name, kind, data in members:
                member = tarfile.TarInfo(name)
                member.mode = 0o644
                member.type = kind
                if kind == tarfile.REGTYPE:
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
                else:
                    member.linkname = data.decode()
                    archive.addfile(member)
        import gzip
        layer = gzip.compress(raw.getvalue())
        digest = lambda value: 'sha256:' + hashlib.sha256(value).hexdigest()
        diff = digest(raw.getvalue())
        config = json.dumps({'os': 'linux', 'architecture': 'arm64', 'rootfs': {'diff_ids': [diff]}}).encode()
        manifest = json.dumps({'config': {'digest': digest(config)}, 'layers': [{
            'digest': digest(layer), 'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip'}]}).encode()
        path = root / 'archive.tar'
        with tarfile.open(path, 'w') as archive:
            for data in [layer, config, manifest]:
                member = tarfile.TarInfo('blobs/' + digest(data).replace(':', '/'))
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        return {'path': str(path), 'actual': {'sha256': digest(path.read_bytes())[7:], 'bytes': path.stat().st_size},
                'request': {'image': {'target': digest(manifest), 'config': digest(config), 'chain': diff}}}

    def exercise(self, members, expected_error=None, cap=512):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            record = self.fixture(root, members)
            with patch.object(materialize, 'SELECTED', {'public/tool'}), patch.object(materialize, 'EXPECTED', {}), patch.object(materialize, 'MAX_BYTES', cap):
                if expected_error:
                    with self.assertRaisesRegex(ValueError, expected_error):
                        materialize.extract(record, root / 'output', time.monotonic() + 2)
                else:
                    result = materialize.extract(record, root / 'output', time.monotonic() + 2)
                    self.assertEqual((root / 'output/public/tool').read_bytes(), b'tool')
                    self.assertEqual(result['linksExtracted'], 0)
                    self.assertFalse(result['rootfsInstalled'])

    def test_selective_regular_file(self):
        self.exercise([('public/tool', tarfile.REGTYPE, b'tool'), ('unselected', tarfile.REGTYPE, b'ignored')])

    def test_root_directory_metadata_is_ignored(self):
        self.exercise([('.', tarfile.DIRTYPE, b''), ('public/tool', tarfile.REGTYPE, b'tool')])

    def test_root_regular_file_is_still_rejected(self):
        self.exercise([('.', tarfile.REGTYPE, b'bad')], 'unsafe-archive-path')

    def test_traversal(self):
        self.exercise([('../outside', tarfile.REGTYPE, b'x')], 'unsafe-archive-path')

    def test_ancestor_links(self):
        for kind in [tarfile.SYMTYPE, tarfile.LNKTYPE]:
            with self.subTest(kind=kind):
                self.exercise([('public', kind, b'outside')], 'ancestor-link')

    def test_whiteout(self):
        self.exercise([('public/.wh.tool', tarfile.REGTYPE, b'')], 'selected-whiteout')

    def test_duplicate_selected_member(self):
        self.exercise([('public/tool', tarfile.REGTYPE, b'tool')] * 2, 'selected-file-replaced')

    def test_cumulative_byte_limit(self):
        self.exercise([('public/tool', tarfile.REGTYPE, b'tool')], 'selected-byte-limit', cap=3)

    def test_missing_selected_member(self):
        self.exercise([('unselected', tarfile.REGTYPE, b'tool')], 'missing-selected-public-file')


if __name__=='__main__':unittest.main()
