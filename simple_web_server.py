import http.server
import socketserver
import os

# Настройте порт и имя файла отчета
PORT = 8000
REPORT_FILE = "ai_result_llama.txt"
ENCODING = "UTF-8"  # Укажите желаемую кодировку

class ReportHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = REPORT_FILE

        try:
            with open(self.path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-type', f'text/plain; charset={ENCODING}')
                self.send_header('Content-length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File Not Found')
        except Exception as e:
            self.send_error(500, f'Internal Server Error: {e}')

if __name__ == "__main__":
    # Проверьте, существует ли файл отчета
    if not os.path.exists(REPORT_FILE):
        print(f"Ошибка: Файл отчета '{REPORT_FILE}' не найден.")
        exit(1)

    with socketserver.TCPServer(("", PORT), ReportHandler) as httpd:
        print(f"Веб-сервер запущен на порту {PORT}. Откройте в браузере: http://localhost:{PORT}")
        httpd.serve_forever()