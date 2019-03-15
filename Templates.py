from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
	return 'Welcome!'


@app.route('/hello')
def hello():
	return render_template('hello.html')


@app.route('/hello/<name>')
def hello_name(name):
	return render_template('hello.html', name=name)


# @app.route('/hello')
# @app.route('/hello/<name>')
# def hello_name(name=None):
# 	return render_template('hello.html', name=name)


if __name__ == '__main__':
	app.run(debug=True)