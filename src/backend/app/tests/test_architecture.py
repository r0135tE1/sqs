from pytestarch import get_evaluable_architecture, Rule
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

evaluable = get_evaluable_architecture(ROOT, APP)


def test_services_do_not_import_routers():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.services")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.routers")
    )
    rule.assert_applies(evaluable)


def test_models_do_not_import_services():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.models")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.services")
    )
    rule.assert_applies(evaluable)


def test_models_do_not_import_routers():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.models")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.routers")
    )
    rule.assert_applies(evaluable)


def test_database_does_not_import_routers():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.database")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.routers")
    )
    rule.assert_applies(evaluable)
