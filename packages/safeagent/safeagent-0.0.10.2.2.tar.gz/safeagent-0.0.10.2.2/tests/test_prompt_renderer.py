# tests/test_prompt_renderer.py
import pytest
from jinja2.exceptions import TemplateNotFound
from pathlib import Path
from safeagent.prompt_renderer import PromptRenderer

@pytest.fixture
def template_dir(tmp_path):
    """Fixture to create a temporary directory with a sample template."""
    d = tmp_path / "templates"
    d.mkdir()
    (d / "test.j2").write_text("Hello, {{ name }}!")
    return d

def test_prompt_renderer_initialization(template_dir):
    """Test that PromptRenderer initializes correctly with a template directory."""
    renderer = PromptRenderer(template_dir=template_dir)
    assert renderer.env is not None
    assert str(template_dir) in str(renderer.env.loader.searchpath)

def test_render_success(template_dir):
    """Test successful rendering of a prompt."""
    renderer = PromptRenderer(template_dir=template_dir)
    # Corrected method call from render_prompt to render
    rendered_text = renderer.render("test.j2", name="World")
    assert rendered_text == "Hello, World!"

def test_render_with_missing_variable(template_dir):
    """Test that rendering with a missing variable works as expected (renders empty)."""
    renderer = PromptRenderer(template_dir=template_dir)
    # Corrected method call
    rendered_text = renderer.render("test.j2")
    assert rendered_text == "Hello, !"

def test_render_template_not_found(template_dir):
    """Test that a TemplateNotFound error is raised for a non-existent template."""
    renderer = PromptRenderer(template_dir=template_dir)
    with pytest.raises(TemplateNotFound):
        # Corrected method call
        renderer.render("nonexistent.j2", name="Test")

def test_governance_audit_is_called_on_render(template_dir):
    """Test that the governance manager's audit method is called during render."""
    renderer = PromptRenderer(template_dir=template_dir)
    
    # Mock the governance manager on the instance
    mock_gov = MagicMock()
    renderer.gov = mock_gov
    
    renderer.render("test.j2", name="AuditMe")
    
    # Assert that audit was called
    mock_gov.audit.assert_called_once()
    call_args, call_kwargs = mock_gov.audit.call_args
    assert call_kwargs['action'] == "prompt_render"
    assert call_kwargs['resource'] == "test.j2"
    assert call_kwargs['metadata']['template'] == "test.j2"
