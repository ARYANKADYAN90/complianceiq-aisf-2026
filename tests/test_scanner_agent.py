import pytest
from src.agents.scanner_agent import ScannerAgent
from src.models.system_profile import SystemProfile


class MockFile:
    def __init__(self, name: str, content: bytes):
        self.name = name
        self.content = content

    def read(self) -> bytes:
        return self.content


@pytest.fixture
def scanner():
    return ScannerAgent(mock_mode=True)


@pytest.mark.asyncio
async def test_extract_text_pdf(mocker, scanner):
    """Test extracting text from PDF file format."""
    mock_pdf_reader = mocker.patch("src.agents.scanner_agent.PdfReader")
    mock_page = mocker.Mock()
    mock_page.extract_text.return_value = "Mock PDF Content"
    mock_pdf_reader.return_value.pages = [mock_page]

    result = await scanner.extract_text(b"fake_pdf_bytes", "test.pdf")
    assert result == "Mock PDF Content"
    mock_pdf_reader.assert_called_once()


@pytest.mark.asyncio
async def test_extract_text_docx(mocker, scanner):
    """Test extracting text from DOCX file format."""
    mock_doc = mocker.patch("src.agents.scanner_agent.Document")
    mock_paragraph = mocker.Mock()
    mock_paragraph.text = "Mock DOCX Content"
    mock_doc.return_value.paragraphs = [mock_paragraph]

    result = await scanner.extract_text(b"fake_docx_bytes", "test.docx")
    assert result == "Mock DOCX Content"
    mock_doc.assert_called_once()


@pytest.mark.asyncio
async def test_extract_text_txt(scanner):
    """Test extracting text from TXT file format."""
    result = await scanner.extract_text(b"Mock TXT Content", "test.txt")
    assert result == "Mock TXT Content"


@pytest.mark.asyncio
async def test_scan_mock_mode(scanner):
    """Test full scan pipeline in mock mode returns valid SystemProfile."""
    files = [
        MockFile("test1.txt", b"Some random text about AI."),
        MockFile("test2.txt", b"More docs."),
    ]

    profile = await scanner.scan(files)

    assert isinstance(profile, SystemProfile)
    assert profile.system_name == "TalentFilter Pro v2.3"
    assert (
        profile.use_case
        == "Automated CV screening and candidate ranking for job applications"
    )
    # raw_text is concatenated from input files
    assert "TalentFilter" in profile.raw_text
    assert "More docs." in profile.raw_text
    # Check confidence is computed
    assert 0.0 <= profile.extraction_confidence <= 1.0


@pytest.mark.asyncio
async def test_scan_empty_files(scanner):
    """Test that scanning empty file list raises ValueError."""
        scanner.mock_mode = False
    with pytest.raises(ValueError, match="No files uploaded"):
        await scanner.scan([])
