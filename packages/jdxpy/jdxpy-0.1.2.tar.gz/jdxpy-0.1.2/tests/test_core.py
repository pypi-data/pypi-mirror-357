"""Tests for jdxpy.core module."""

from jdxpy.core import hello_jdxpy


class TestHelloJdxPy:
    """hello_jdxpy関数のテストクラス."""

    def test_hello_jdxpy_returns_string(self):
        """基本的な戻り値のテスト."""
        result = hello_jdxpy()
        assert isinstance(result, str)
        assert result == "Hello from JDxPy!"

    def test_hello_jdxpy_consistent_output(self):
        """一貫した出力のテスト."""
        result1 = hello_jdxpy()
        result2 = hello_jdxpy()
        assert result1 == result2

    def test_hello_jdxpy_not_empty(self):
        """空でない文字列を返すことのテスト."""
        result = hello_jdxpy()
        assert len(result) > 0
        assert result.strip() != ""

    def test_hello_jdxpy_contains_expected_text(self):
        """期待されるテキストが含まれることのテスト."""
        result = hello_jdxpy()
        assert "Hello" in result
        assert "JDxPy" in result
