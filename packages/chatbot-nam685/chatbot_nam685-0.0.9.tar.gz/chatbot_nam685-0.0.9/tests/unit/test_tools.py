from chatbot.utils.tools.multiply import multiply


def test_multiply_function():
    result = multiply.invoke({"a": 3, "b": 4})
    assert result == 12
