class ReportBuilder:
    def __init__(self, race_result):
        self.race_result = race_result

    def build_report(self, top_n=15, ascending=True):
        """
        Повертає структурований список топ-гонщиків і решти.
        """
        sorted_results = self.race_result.get_sorted_results(ascending)
        top = sorted_results[:top_n]
        rest = sorted_results[top_n:]
        return {"top": top, "rest": rest}

    def format_time(self, delta):
        """
        Форматує об'єкт timedelta у вигляді MM:SS.mmm
        """
        minutes, seconds = divmod(delta.total_seconds(), 60)
        milliseconds = delta.microseconds // 1000
        return f"{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

    def format_report(self, report_data):
        """
        Форматує звіт у вигляді рядків.
        """
        report_lines = []
        for i, result in enumerate(report_data["top"], start=1):
            formatted_time = self.format_time(result["time"])
            report_lines.append(f"{i}. {result['name']} | {result['team']} | {formatted_time}")

        report_lines.append("-" * 72)

        for i, result in enumerate(report_data["rest"], start=len(report_data["top"]) + 1):
            formatted_time = self.format_time(result["time"])
            report_lines.append(f"{i}. {result['name']} | {result['team']} | {formatted_time}")

        return "\n".join(report_lines)

    def build_driver_report(self, driver_name):
        """
        Створює звіт для конкретного гонщика.
        """
        for result in self.race_result.results:
            if result["name"] == driver_name:
                formatted_time = self.format_time(result["time"])
                return (
                    f"Звіт для гонщика {driver_name}:\n"
                    f"Ім'я: {result['name']}\n"
                    f"Команда: {result['team']}\n"
                    f"Час: {formatted_time}\n"
                )
        return f"Гонщик з іменем {driver_name} не знайдений у результатах."
