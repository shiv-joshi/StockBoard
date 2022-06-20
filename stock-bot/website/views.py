from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Stock
from . import db
import json

import yahoofinancials as yfs
from yahoofinancials import YahooFinancials
import alpaca_trade_api as tradeapi
alpaca_endpoint = 'https://paper-api.alpaca.markets'

class pythonBuyBot():
    def __init__(self):
        self.alpaca = tradeapi.REST('PK0ZRSZMRN29GQLBP3ST','HvT4dFZYeWBJ6RVQhDtKVWMFREYjWsMWohbSn54Y', alpaca_endpoint)

    def buyOrder(self, symbol, qty, side):
        self.alpaca.submit_order(symbol, qty, side, "market", "gtc")

    def sellOrder(self, symbol, qty, side):
        self.alpaca.submit_order(symbol, qty, side, "market", "gtc")
        
    def balance(self):
        account = self.alpaca.get_account()
        curr = float(account.buying_power)

        current_user.balance = curr
        db.session.commit()
    
    def get_prices(self):
        for s in current_user.stocks:
            yfs = YahooFinancials(s.stock)
            s.current_price = yfs.get_current_price
            db.session.commit()

                
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        stock = request.form.get('stock')
        qty = request.form.get('quantity')
        side = request.form.get('side')

        existing = Stock.query.join(User.stocks).filter(User.id==current_user.id, Stock.stock==stock).first()

        if side == 'buy':
            if existing:
                existing.quantity = existing.quantity + int(qty)
                db.session.commit()
            else:  
                try:
                    yfs = YahooFinancials(stock)

                    if qty!=0:
                        pb = pythonBuyBot() 
                        pb.buyOrder(stock, qty, 'buy')
                        
                        new_stock = Stock(stock=stock, quantity=qty, user_id=current_user.id)
                        
                        db.session.add(new_stock)
                        db.session.commit()
                        flash(qty+" shares of "+stock+" purchased!", category='success')
                    else:
                        flash("Error: number of shares cannot be 0.", category='error')
                except:
                    response = "Error occurred, please make sure you have entered valid input.(number of shares cannot be 0)"
                    flash(response, category='error')
        elif side == 'sell':
            if existing:
                if existing.user_id == current_user.id:
                    if existing.quantity > int(qty):
                        existing.quantity = existing.quantity - int(qty)
                        db.session.commit()

                        try:
                            pb = pythonBuyBot() 
                            pb.sellOrder(stock, qty, 'sell')
                        except:
                            pass

                        flash(qty+" shares of "+stock+" sold!",category="success")
                    elif existing.quantity == int(qty):
                        existing.quantity = existing.quantity - int(qty)
                        db.session.commit()

                        try:
                            pb = pythonBuyBot() 
                            pb.sellOrder(stock, qty, 'sell')
                        except:
                            pass

                        #delete from db
                        db.session.delete(stock)
                        db.session.commit()

                        flash(qty+" shares of "+stock+" sold!",category="success")
                    elif existing.quantity < int(qty):
                        flash("You do not own that number of shares in "+stock,category="error")
        else:
            flash("Please enter valid input", category="error")

    pb = pythonBuyBot()
    pb.balance()
    
    return render_template("home.html", user=current_user)







@views.route('/delete-note', methods=['POST'])
def delete_note():
    stock = json.loads(request.data)
    stockId = stock['stockId']
    stock = Stock.query.get(stockId)
    if stock:
        if stock.user_id == current_user.id:
            #delete from db
            db.session.delete(stock)
            db.session.commit()
            
    return jsonify({})