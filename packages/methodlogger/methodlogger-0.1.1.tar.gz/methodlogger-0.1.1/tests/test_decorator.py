from methodlogger.decorators import log_method

class Demo:
    @log_method("🔧 Demo method running")
    def work(self):
        return "ok"

def test_work():
    d = Demo()
    assert d.work() == "ok"
