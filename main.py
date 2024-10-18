from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from utils.ast_utils import parse_rule_string, combine_nodes, evaluate, print_tree , node_to_dict
import random
import string
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
import logging

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///rules.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), unique=True, nullable=False)
    rule_ast = db.Column(db.PickleType, nullable=False)


def generate_random_letter_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


@app.route('/')
def serve_index():
    return render_template('index.html')


@app.route('/api/rules/create_rule', methods=['POST'])
def create_rule():
    try:
        data = request.json
        rule_name = data.get('ruleName')
        rule_string = data.get('ruleString')

        logger.info(f"Received create_rule request. Rule name: {rule_name}, Rule string: {rule_string}")

        if not rule_name or not rule_string:
            return jsonify({'error': 'ruleName and ruleString are required'}), 400

        try:
            root_node = parse_rule_string(rule_string)
        except ValueError as e:
            logger.error(f"Error parsing rule string: {str(e)}")
            return jsonify({'error': f'Error parsing rule string: {str(e)}'}), 400

        rule = Rule(rule_name=rule_name, rule_ast=root_node)

        try:
            db.session.add(rule)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': f'A rule with the name "{rule_name}" already exists'}), 409

        logger.info(f"Successfully created rule. Rule name: {rule_name}, Rule ID: {rule.id}")
        print_tree(root_node)
        return jsonify({'ruleName': rule.rule_name, 'id': rule.id, 'tree': node_to_dict(root_node)}), 201
    except Exception as error:
        logger.error(f"Unexpected error in create_rule: {str(error)}", exc_info=True)
        return jsonify({'error': str(error)}), 500


@app.route('/api/rules/combine_rules', methods=['POST'])
def combine_rules():
    try:
        data = request.json
        rules = data.get('rules')
        op = data.get('op')

        rule_docs = Rule.query.filter(Rule.rule_name.in_(rules)).all()
        if not rule_docs:
            return jsonify({'error': 'No matching rules found'}), 404

        rule_asts = [rule.rule_ast for rule in rule_docs]
        combined_root_node = combine_nodes(rule_asts, op)

        random_string = generate_random_letter_string(4)
        new_rule_name = f'combined{random_string}'
        rule = Rule(rule_name=new_rule_name, rule_ast=combined_root_node)
        db.session.add(rule)
        db.session.commit()

        print_tree(combined_root_node)
        return jsonify({'ruleName': rule.rule_name, 'id': rule.id, 'tree': node_to_dict(combined_root_node)}), 201
    except Exception as error:
        logger.error(f"Error in combine_rules: {str(error)}", exc_info=True)
        return jsonify({'error': str(error)}), 500


@app.route('/api/rules/evaluate_rule', methods=['POST'])
def evaluate_rule():
    try:
        data = request.json
        ast_name = data.get('ast')
        eval_data = data.get('data')

        rule = Rule.query.filter_by(rule_name=ast_name).first()
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404

        result = evaluate(rule.rule_ast, eval_data)
        return jsonify({'result': result, 'tree': node_to_dict(rule.rule_ast)}), 200
    except Exception as error:
        logger.error(f"Error in evaluate_rule: {str(error)}", exc_info=True)
        return jsonify({'error': str(error)}), 500


@app.route('/api/rules/get_rule_tree/<rule_identifier>', methods=['GET'])
def get_rule_tree(rule_identifier):
    try:
        if rule_identifier.isdigit():
            rule = Rule.query.get(int(rule_identifier))
        else:
            rule = Rule.query.filter_by(rule_name=rule_identifier).first()

        if not rule:
            return jsonify({'error': 'Rule not found'}), 404

        return jsonify({'tree': node_to_dict(rule.rule_ast)}), 200
    except Exception as error:
        logger.error(f"Error in get_rule_tree: {str(error)}", exc_info=True)
        return jsonify({'error': str(error)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)