"""Bounded preparation input controls: no builds, rendering, or original file edits."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import prepare
from prepare_inputs import validate_inputs, SOURCE_DIGEST

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
CATALOG = REPO / "build/catalog-host"

class PrepareInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (CATALOG / "patched/identity.json").is_file():
            raise unittest.SkipTest("prepare the frozen catalog first; these controls use its retained source bytes")
        cls.identity = json.loads((CATALOG / "patched/identity.json").read_text())
        cls.actual_source = Path(cls.identity["source"])
        cls.expected = json.loads((REPO / "docs/superpowers/evidence/patch-visual-catalog/patched-source-tree.json").read_text())

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="i31-prepare-control-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.catalog = self.base / "catalog"
        self.source = self.base / "source"
        self.evidence = self.base / "evidence"
        self.work = self.base / "output"
        # Link read-only bytes into private temporary fixtures. Mutation controls
        # replace/remove the link itself, never write through to original inputs.
        for relative in self.expected:
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(self.actual_source / relative)
        for original, target in ((CATALOG / "harness", self.catalog / "harness"),
                                 (ROOT / "harness", self.evidence / "harness"),
                                 (ROOT / "image-harness", self.evidence / "image-harness")):
            for file in original.rglob("*"):
                if file.is_file():
                    link = target / file.relative_to(original)
                    link.parent.mkdir(parents=True, exist_ok=True)
                    link.symlink_to(file)
        self.identity = {**self.identity, "source": str(self.source)}
        (self.catalog / "patched").mkdir()
        self.write_identity()

    def write_identity(self):
        (self.catalog / "patched/identity.json").write_text(json.dumps(self.identity))

    def replace(self, path, data):
        if path.is_symlink(): path.unlink()
        path.write_bytes(data)

    def reject_before_output(self):
        with patch.object(prepare.subprocess, "run") as run, patch.object(prepare.subprocess, "check_output") as git:
            with self.assertRaises(ValueError):
                prepare.prepare(REPO, self.catalog, self.work, self.evidence)
            self.assertFalse(self.work.exists())
            run.assert_not_called()
            git.assert_not_called()

    def test_valid_actual_source_and_harness_bytes(self):
        identity, expected = validate_inputs(REPO, self.catalog, self.evidence)
        self.assertEqual(expected, self.expected)
        self.assertEqual(Path(identity["source"]), self.source)

    def test_changed_source_rejects_before_output_or_build(self):
        self.replace(self.source / "src/libprojectM/MilkdropPreset/VideoEcho.cpp", b"arbitrary edited renderer")
        self.reject_before_output()

    def test_missing_or_extra_source_rejects_before_output_or_build(self):
        for mutation in ("missing", "extra"):
            with self.subTest(mutation=mutation):
                file = self.source / ".clang-format" if mutation == "missing" else self.source / "extra.cpp"
                if mutation == "missing": file.unlink()
                else: file.write_text("extra source")
                self.reject_before_output()
                if mutation == "missing": file.symlink_to(self.actual_source / ".clang-format")
                else: file.unlink()

    def test_coherent_source_receipt_change_still_rejects(self):
        self.replace(self.source / ".clang-format", b"changed bytes")
        self.identity["source_tree_sha256"] = SOURCE_DIGEST
        self.write_identity()
        (self.catalog / "patched/source-tree.json").write_text(json.dumps(self.expected))
        self.reject_before_output()

    def test_changed_catalog_vendor_rejects_before_output(self):
        self.replace(self.catalog / "harness/vendor/json.hpp", b"changed JSON dependency")
        self.reject_before_output()

    def test_changed_observer_templates_reject_before_output(self):
        for directory in ("harness", "image-harness"):
            with self.subTest(directory=directory):
                file = self.evidence / directory / "worker.cpp"
                self.replace(file, b"changed observer source")
                self.reject_before_output()
                file.unlink()
                file.symlink_to(ROOT / directory / "worker.cpp")

    def test_wrong_engine_pin_rejects_before_output(self):
        self.identity["engine"] = {**self.identity["engine"], "commit": "0" * 40}
        self.write_identity()
        self.reject_before_output()

    def test_full_builder_identity_with_correct_manifest_is_admitted(self):
        self.identity.update(source_tree_sha256=SOURCE_DIGEST,
                             evaluator_commit="22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a",
                             host={"system": "Darwin", "machine": "arm64"})
        self.write_identity()
        (self.catalog / "patched/source-tree.json").write_text(json.dumps(self.expected))
        validate_inputs(REPO, self.catalog, self.evidence)

    def test_copied_source_race_rejects_before_observer_or_build(self):
        # Supply the other copied adapters used before the engine copy check.
        (self.evidence / "link_images.py").symlink_to(ROOT / "link_images.py")
        original_copy = shutil.copytree
        def changed_copy(source, destination, *args, **kwargs):
            result = original_copy(source, destination, *args, **kwargs)
            if Path(destination).name == "engine":
                (Path(destination) / ".clang-format").write_text("changed after snapshot")
            return result
        patch_bytes = (REPO / "tools/projectm-patches/0019-gamma-only-pass-epsilon.patch").read_bytes()
        with patch.object(prepare.shutil, "copytree", side_effect=changed_copy), patch.object(prepare.subprocess, "run") as run, patch.object(prepare.subprocess, "check_output", return_value=patch_bytes):
            with self.assertRaisesRegex(ValueError, "actual engine source differs"):
                prepare.prepare(REPO, self.catalog, self.work, self.evidence)
            run.assert_not_called()

    def test_copied_vendor_race_rejects_before_git_or_build(self):
        original_copy = shutil.copytree
        def changed_copy(source, destination, *args, **kwargs):
            result = original_copy(source, destination, *args, **kwargs)
            destination = Path(destination)
            if destination.name == "vendor" and destination.parent.name == "image-harness":
                (destination / "json.hpp").write_text("changed copied vendor")
            return result
        with patch.object(prepare.shutil, "copytree", side_effect=changed_copy), patch.object(prepare.subprocess, "run") as run, patch.object(prepare.subprocess, "check_output") as git:
            with self.assertRaisesRegex(ValueError, "copied image-harness/vendor inputs changed"):
                prepare.prepare(REPO, self.catalog, self.work, self.evidence)
            run.assert_not_called()
            git.assert_not_called()
