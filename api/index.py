from flask import Flask, request, jsonify, render_template
from json import dumps
from httplib2 import Http
import os

def send_message(message):
  url = os.environ.get('CHAT_WEBHOOK_URL')
  if not url:
      print("Available environment variables:", list(os.environ.keys()))
      raise ValueError(f"CHAT_WEBHOOK_URL is not set or is empty")
  app_message = {
    "text": message,
  }
  message_headers = {"Content-Type": "application/json; charset=UTF-8"}
  http_obj = Http()
  response = http_obj.request(
    uri=url,
    method="POST",
    headers=message_headers,
    body=dumps(app_message),
  )
  return response

app = Flask(__name__)

@app.route('/')
def hello():
  return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
  message = request.form['message']
  res = send_message(message)
  return str(res)

@app.route('/openai', methods=['GET', 'POST'])
def openai():
    data = request.get_json()
    if not data:
        return "No data received", 400

    # Extract relevant information
    page_info = data.get('page', {})
    status_indicator = page_info.get('status_indicator')
    status_description = page_info.get('status_description')

    # Handle component updates
    if 'component_update' in data:
        component = data.get('component', {})
        component_update = data.get('component_update', {})
        message = (
            f"*OPENAI STATUS UPDATE ⚠️*\n"
            f"*Component*: {component.get('name')}\n"
            f"*Status*: {component_update.get('old_status')} → {component_update.get('new_status')}"
        )
        send_message(message)

    # Handle incidents
    if 'incident' in data:
        incident = data.get('incident', {})
        updates = incident.get('incident_updates', [])
        latest_update = updates[0] if updates else {}
        
        message = (
            f"*OPENAI STATUS UPDATE ⚠️*\n"
            f"*Incident Update*: {incident.get('name')}\n"
            f"*Status*: {incident.get('status')}\n"
            f"*Impact*: {incident.get('impact')}\n"
            f"*Latest Update*: {latest_update.get('body')}"
        )
        send_message(message)

    return jsonify({
        "status": "success",
        "received_status": status_indicator,
        "description": status_description
    }), 200

@app.route('/robot-button-down', methods=['POST'])
def robot_button_down():
  json = request.get_json()
  button = json.get('button')
  send_message("😲 *A BUTTON HAS BEEN PRESSED*\nType: down\nButton: {}".format(button))
  return "OK"

@app.route('/robot-button-up', methods=['POST'])
def robot_button_up():
  json = request.get_json()
  button = json.get('button')
  send_message("😲 *A BUTTON HAS BEEN UNPRESSED*\nType: up\nButton: {}".format(button))
  return "OK"

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
