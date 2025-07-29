"""Tests for dx_py.core module."""

from dx_py.core import hello_dxpy


class TestHelloDxPy:
    """hello_dxpy関数のテストクラス."""

    def test_hello_dxpy_returns_string(self):
        """基本的な戻り値のテスト."""
        result = hello_dxpy()
        assert isinstance(result, str)
        assert result == "Hello from DxPy!"

    def test_hello_dxpy_consistent_output(self):
        """一貫した出力のテスト."""
        result1 = hello_dxpy()
        result2 = hello_dxpy()
        assert result1 == result2

    def test_hello_dxpy_not_empty(self):
        """空でない文字列を返すことのテスト."""
        result = hello_dxpy()
        assert len(result) > 0
        assert result.strip() != ""

    def test_hello_dxpy_contains_expected_text(self):
        """期待されるテキストが含まれることのテスト."""
        result = hello_dxpy()
        assert "Hello" in result
        assert "DxPy" in result
