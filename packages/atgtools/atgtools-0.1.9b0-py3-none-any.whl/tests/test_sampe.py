import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from atg.tools.sampe import subsample_fastq


@patch('atg.tools.sampe.pyfastx.Fastx')
def test_subsample_fastq(mock_fastx, tmp_path):
    mock_fx = MagicMock()
    mock_fx.__len__.return_value = 100
    mock_fx.__getitem__.return_value.raw = "@test\nACGT\n+\n!!!!\n"
    mock_fastx.return_value = mock_fx
    
    input_file = tmp_path / "sample.fastq.gz"
    input_file.write_text("test content")
    output_dir = tmp_path / "output"
    
    subsample_fastq(str(input_file), str(output_dir), 0.5, seed=42)
    
    assert output_dir.exists()
    output_files = list(output_dir.glob("*"))
    assert len(output_files) == 1
    assert "subsample" in output_files[0].name
