#!/usr/bin/env python3
import importlib.util
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_baseline_module():
    spec = importlib.util.spec_from_file_location(
        "check_baseline", ROOT / "scripts" / "check-baseline.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline = load_baseline_module()


class MakefileRootTests(unittest.TestCase):
    def run_make(self, *arguments, environment=None):
        with tempfile.TemporaryDirectory(prefix="Oscars Stream's [gate] ") as directory:
            checkout = Path(directory)
            makefile = checkout / "Makefile"
            makefile.write_text(
                (ROOT / "Makefile").read_text(encoding="utf-8"), encoding="utf-8"
            )
            env = {"PATH": os.environ.get("PATH", "")}
            if environment:
                env.update(environment)
            result = subprocess.run(
                ["make", "--no-print-directory", "-n", "-f", str(makefile), *arguments],
                cwd=checkout.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                env=env,
            )
            return result, shlex.quote(str(checkout.resolve()))

    def assert_live_root_path_is_literal(self, checkout_name, marker_name):
        with tempfile.TemporaryDirectory() as parent:
            checkout = Path(parent) / checkout_name
            scripts = checkout / "scripts"
            scripts.mkdir(parents=True)
            makefile = checkout / "Makefile"
            makefile.write_text(
                (ROOT / "Makefile").read_text(encoding="utf-8"), encoding="utf-8"
            )
            (scripts / "test-makefile-root.py").write_text(
                "print('live root stub passed')\n", encoding="utf-8"
            )
            result = subprocess.run(
                ["make", "--no-print-directory", "-f", str(makefile), "root-test"],
                cwd=checkout.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                env={"PATH": os.environ.get("PATH", "")},
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertFalse((checkout.parent / marker_name).exists(), result.stdout)
            self.assertIn("live root stub passed", result.stdout)

    def test_all_targets_preserve_spaced_absolute_makefile_path(self):
        targets = ("build", "check", "lint", "root-test", "static-check", "test", "verify")
        for target in targets:
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "REPO_ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"REPO_ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result, expected_root = self.run_make(*arguments, environment=environment)
                    self.assertEqual(result.returncode, 0, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)
                    self.assertIn(expected_root, result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("verify", "MAKEFILE_LIST=/tmp/untrusted")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_environment_makefile_list_override_fails_closed(self):
        result, _ = self.run_make("-e", "verify", environment={"MAKEFILE_LIST": "/tmp/untrusted"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stdout)

    def test_live_root_path_does_not_execute_shell_metacharacters(self):
        for checkout_name, marker_name in (
            ("Oscars backtick `touch BACKTICK_PWNED` case", "BACKTICK_PWNED"),
            ('Oscars quote " ; touch QUOTE_PWNED ; echo " case', "QUOTE_PWNED"),
        ):
            with self.subTest(checkout_name=checkout_name):
                self.assert_live_root_path_is_literal(checkout_name, marker_name)


class MakefileRecipePinTests(unittest.TestCase):
    """Planted-defect controls for the exact-recipe pin.

    Each mutation is applied to real Makefile text and the pin is executed, so a
    green result here means the pin ran and produced a verdict rather than that
    a harness merely reported one.
    """

    def setUp(self):
        self.makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    def test_live_makefile_recipes_satisfy_the_pin(self):
        self.assertEqual([], baseline.makefile_recipe_failures(self.makefile))

    def test_pin_parses_every_expected_gate_recipe(self):
        recipes = baseline.makefile_recipes(self.makefile)
        for target, expected in baseline.EXPECTED_MAKEFILE_RECIPES.items():
            self.assertEqual(expected, recipes.get(target), target)

    def test_pin_rejects_exit_status_neutering_on_every_gate_recipe(self):
        for target, expected in baseline.EXPECTED_MAKEFILE_RECIPES.items():
            for suffix in (" || true", " ; true", " || exit 0"):
                with self.subTest(target=target, suffix=suffix):
                    mutated = self.makefile.replace(
                        "\t" + expected[0] + "\n",
                        "\t" + expected[0] + suffix + "\n",
                        1,
                    )
                    self.assertNotEqual(self.makefile, mutated, "mutation must apply")
                    failures = baseline.makefile_recipe_failures(mutated)
                    self.assertTrue(failures, f"{target}{suffix} must be rejected")
                    self.assertIn(f"Makefile target {target} must run exactly", failures[0])

    def test_pin_rejects_silenced_and_ignored_recipe_prefixes(self):
        expected = baseline.EXPECTED_MAKEFILE_RECIPES["test"][0]
        for prefix in ("@echo ", "-"):
            with self.subTest(prefix=prefix):
                mutated = self.makefile.replace(
                    "\t" + expected + "\n", "\t" + prefix + expected + "\n", 1
                )
                self.assertNotEqual(self.makefile, mutated, "mutation must apply")
                self.assertIn(
                    "Makefile target test must run exactly",
                    " ".join(baseline.makefile_recipe_failures(mutated)),
                )

    def test_pin_rejects_deleted_and_relocated_gate_recipe(self):
        expected = baseline.EXPECTED_MAKEFILE_RECIPES["static-check"][0]
        deleted = self.makefile.replace("\t" + expected + "\n", "", 1)
        self.assertNotEqual(self.makefile, deleted, "mutation must apply")
        self.assertIn(
            "Makefile target static-check must run exactly",
            " ".join(baseline.makefile_recipe_failures(deleted)),
        )
        relocated = deleted + "unused-target:\n\t" + expected + "\n"
        self.assertIn(
            "Makefile target static-check must run exactly",
            " ".join(baseline.makefile_recipe_failures(relocated)),
        )

    def test_workflow_keeps_direct_out_of_band_gate_steps(self):
        workflow_lines = [
            line.strip()
            for line in (ROOT / ".github/workflows/check.yml")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        for step in baseline.EXPECTED_DIRECT_CI_STEPS:
            self.assertIn(step, workflow_lines)


if __name__ == "__main__":
    unittest.main()
