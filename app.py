# app.py
from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # sesuaikan dengan username MySQL Anda
        password="",  # sesuaikan dengan password MySQL Anda
        database="sistem_pakar_pencurian"
    )

def forward_chaining(answers):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM aturan"
    cursor.execute(query)
    rules = cursor.fetchall()

    relevant_pasal_ids = []
    for rule in rules:
        if rule['kondisi'] in answers:
            relevant_pasal_ids.append(rule['pasal_id'])

    if relevant_pasal_ids:
        placeholders = ', '.join(['%s'] * len(relevant_pasal_ids))
        cursor.execute(f"SELECT * FROM pasal_pencurian WHERE id IN ({placeholders})", relevant_pasal_ids)
        pasal_list = cursor.fetchall()

        if pasal_list:
            pasal_terberat = None
            for pasal in pasal_list:
                hukuman_max = pasal['hukuman_max']
                if hukuman_max in ['seumur hidup', 'mati']:
                    pasal_terberat = pasal
                    break
                elif pasal_terberat is None or int(hukuman_max.split()[0]) > int(pasal_terberat['hukuman_max'].split()[0]):
                    pasal_terberat = pasal
            return pasal_terberat

    cursor.close()
    connection.close()
    return None

@app.route('/practice')
def practice():
    return render_template('practice.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/practice_result', methods=['POST'])
def practice_result():
    answers = request.form.getlist('answers')
    result = forward_chaining(answers)
    return render_template('practice_result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
