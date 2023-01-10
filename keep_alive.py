"""from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "Hi, I am alive!"

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()"""

import keep_alive
from threading import Thread
from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask('')

@app.route('/')
def main():
    return render_template('index.html')

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()