from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('welcome.html')


@app.route('/preference', methods=['POST', 'GET'])
def index():
    return render_template('choice.html')


@app.route('/handle_form', methods=['POST', 'GET'])
def handle_form():
    headers = {'Authorization': 'Bearer %s' % 'boovLwU4BPpx-X7tEPWSbQvHQkkAGp_g3lHxukYM9SAGtgWpkrkRc-VKL-HddKAAU34rF84x_2Ji301y470F6GwaXjAxUMtslVfNsamfSpLbkiuPDllhszvP3AxOYnYx'}

    user_address = request.form["address"]  # str
    food_types_list = request.form.getlist('like_types')    # list
    food_price = request.form["price"]  # str

    food_types = ",".join(food_types_list).lower()  # convert list into str
    base_url = "https://api.yelp.com/v3/businesses/search?location="+user_address+"&categories="+food_types+"&price="+food_price
    resp_address = requests.get("https://api.yelp.com/v3/businesses/search?location="+user_address+"&categories="+food_types+"&price="+food_price, headers=headers)
    json_str = resp_address.text    # JSON string
    # json.loads(json_str) is a dictionary
    info_list = json.loads(json_str)['businesses']  # list of dictionary

    global table_name
    table_name = "table_"+user_address
    if os.path.exists(table_name):
        os.remove(table_name)

    with open(table_name, "w") as final:
        json.dump(info_list, final)
    return redirect(url_for('process_data'))

def isLeaf(tree):
    parent = tree[0]
    left_child = tree[1]
    right_child = tree[2]
    if left_child is None and right_child is None:
        return True
    else:
        return False

def playLeaf(tree):
    parent = tree[0]
    left_child = tree[1]
    right_child = tree[2]
    return parent

def simplePlay(tree):
    parent = tree[0]
    left_child = tree[1]
    right_child = tree[2]
    if isLeaf(tree) is False:
        print(parent)
        ans = input("Your answer: ")
        if ans.lower() == "yes":
            return simplePlay(left_child)
        if ans.lower() == "no":
            return simplePlay(right_child)
    else:
        return playLeaf(tree)

def printTree(tree, prefix = '', bend = '', answer = ''):
    """Recursively print a 20 Questions tree in a human-friendly form.
       TREE is the tree (or subtree) to be printed.
       PREFIX holds characters to be prepended to each printed line.
       BEND is a character string used to print the "corner" of a tree branch.
       ANSWER is a string giving "Yes" or "No" for the current branch."""
    text, left, right = tree
    if left is None  and  right is None:
        print(f'{prefix}{bend}{answer}It is {text}')
    else:
        print(f'{prefix}{bend}{answer}{text}')
        if bend == '+-':
            prefix = prefix + '| '
        elif bend == '`-':
            prefix = prefix + '  '
        printTree(left, prefix, '+-', "Yes: ")
        printTree(right, prefix, '`-', "No:  ")


@app.route('/process_data', methods=['GET', 'POST'])
def process_data():
    open_file = open(table_name, "r")
    a = json.loads(open_file.read())
    open_file.close()
    a_sort_dist = sorted(a, key=lambda x: x['distance'])

    flag = True
    while flag:

        Tree = \
            ("Do you have specific restaurant?",
             ("Is it " + a_sort_dist[0]['name'] +"?",
              ('I got it', None, None),
              ('distance?',
               ('Adjust distance for you', None, None),
               ('rating?', ('Adjust rating for you', None, None),
                ('price?', ('Adjust price for you', None, None),
                 ('Delivery?', ('select delivery for you', None, None), ('select pickup for you', None, None)))))),
             (redirect('/preference'), None, None))

        printTree(Tree)
        output = simplePlay(Tree)

        if output == 'I got it':
            return redirect(a_sort_dist[0]['url'])
        elif output.split()[1] == 'distance':
            a_sort_dist.pop(0)
        elif output.split()[1] == 'rating':
            a_sort_dist.pop(0)
            a_sort_dist = sorted(a_sort_dist, key=lambda x: (-x['rating'], x['distance']))
        elif output.split()[1] == 'price':
            a_sort_dist.pop(0)
            a_sort_dist = sorted(a_sort_dist, key=lambda x: (x['price'], x['distance']))
        elif output.split()[1] == 'delivery':
            a_sort_dist.pop(0)
            a_sort_dist = list(filter(lambda i: i['transactions'] == ['delivery'] or i['transactions'] == ['delivery', 'pickup'], a_sort_dist))
        elif output.split()[1] == 'pickup':
            a_sort_dist.pop(0)
            a_sort_dist = list(filter(lambda i: i['transactions'] == ['pickup'] or i['transactions'] == ['delivery', 'pickup'], a_sort_dist))



    return str(0)


# name, categories, distance, price, rating, transactions
# image_url,



if __name__ == '__main__':
    app.run(debug=True)