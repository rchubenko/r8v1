from r8_foundation.check_docs import (
    check_adrs,
    check_architecture_constants,
    check_links,
    check_required,
)


def test_required_documents_exist() -> None:
    assert check_required() == []


def test_active_adr_index_is_complete_and_unique() -> None:
    assert check_adrs() == []


def test_internal_markdown_links_resolve() -> None:
    assert check_links() == []


def test_machine_checkable_architecture_baseline_passes() -> None:
    assert check_architecture_constants() == []
