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


def test_services_do_not_import_database():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.services")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.database")
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


def test_models_do_not_import_database():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.models")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.database")
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


def test_database_models_do_not_import_pydantic_models():
    rule = (
        Rule()
        .modules_that()
        .are_named("backend.app.database.models")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.models")
    )
    rule.assert_applies(evaluable)


def test_config_does_not_import_internal_modules():
    rule = (
        Rule()
        .modules_that()
        .are_named("backend.app.config")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app")
    )
    rule.assert_applies(evaluable)


def test_dependencies_do_not_import_routers():
    rule = (
        Rule()
        .modules_that()
        .are_named("backend.app.dependencies")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.routers")
    )
    rule.assert_applies(evaluable)



def test_routers_do_not_import_database():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.routers")
        .should_not()
        .import_modules_that()
        .are_sub_modules_of("backend.app.database")
    )
    rule.assert_applies(evaluable)


def test_services_do_not_import_dependencies():
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of("backend.app.services")
        .should_not()
        .import_modules_that()
        .are_named("backend.app.dependencies")
    )
    rule.assert_applies(evaluable)
