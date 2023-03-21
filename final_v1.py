from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import json
import requests
from web3 import Web3
from web3.exceptions import TransactionNotFound
import time

# Configuración
INFURA_API_KEY = "f20e0826dc694fc0b8b10a4ded50c259"
PRIVATE_KEY = "46771f346e5d7d28bdbd430ba8c6040fd4daa7e7426d200632f9710af537aa1d"
YOUR_ETH_ADDRESS = "0x09E7D5492cB9B9655C83fE2bBE4b2333e31927d5"

TO_ADDRESS = "0x09E7D5492cB9B9655C83fE2bBE4b2333e31927d5"
TO_CHAIN_ID = 56

w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_API_KEY}'))
w3.eth.account.enable_unaudited_hdwallet_features()

# Carga del ABI del contrato Router
router_abi_url = "https://bridgeapi.anyswap.exchange/routerabi"
router_abi = json.loads(requests.get(router_abi_url).text)

TOKEN = "6058904432:AAEYX5x6IBvvORMkolo3dS-7lX88cNiYBwU"

user_data = {
    "user_private_key": "",
    "from_wallet": "",
    "user_token": "",
    "to_wallet": "",
    "from_network": "",
    "to_network": "",
    "amount": "",
}

def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to BridgeHub Bot",
    )
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://imgur.com/Bljg3jt",
    )
    keyboard = [
        [
            InlineKeyboardButton("Private Key", callback_data="button_1"),
            InlineKeyboardButton("Your Wallet", callback_data="button_2"),
        ],
        [
            InlineKeyboardButton("Token", callback_data="button_3"),
            InlineKeyboardButton("Target Wallet", callback_data="button_4"),
        ],
        [
            InlineKeyboardButton("Network", callback_data="button_5"),
            InlineKeyboardButton("To Network", callback_data="button_6"),
        ],
        [
            InlineKeyboardButton("Amount", callback_data="button_7"),
            InlineKeyboardButton("🗑 Clear Data", callback_data="clear_data"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("<b><u>🔗Steps to create a Bridge on BridgeHub:</u></b>\n\n 1.Enter your <b><u>private key</u></b> <i>(to sign both the bridge and approval contract)</i>\n 2.<b>Your wallet and destination wallet</b> are required.\n 3.You need to specify the <b>Token</b> <i>(available only USDC and ETH)</i>\n 4.Choose the starting and <b>destination blockchain network</b> (available ERC20 and BEP20 network)\n 5.Enter the <b>amount of ETH or USDC</b> you want to transfer through the bridge.\n\n<b><i>Note: You can clear the entered data by clicking '🗑Clear Data' </i></b>", reply_markup=reply_markup, parse_mode="html")

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data["current_button"] = query.data
    query.answer()
    
    if query.data == "button_1":
        text = "Type your private key"
    elif query.data == "button_2":
        text = "Type your wallet address"
    elif query.data == "button_3":
        text = "With which token do you want to bridge? (USDC or ETH)"
    elif query.data == "button_4":
        text = "Type the destination wallet"
    elif query.data == "button_5":
        text = "Type the network from which you will do the Bridge (BSC or ETH)"
    elif query.data == "button_6":
        text = "Enter the network where you want to receive the tokens (BSC or ETH)"
    elif query.data == "button_7":
        text = "Enter the amount\nMinimun USDC Amount: $12\nMinimun ETH Amount (Example: \n-In case of USDC, type a number such as 15, 20..\n-For ETH just type something like 0.01, 0.05, 1...)"
    
    query.edit_message_text(text=f"{text}:")

def clear_data_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "clear_data":
        context.user_data.clear()
        query.answer(text="Every data was removed")
        query.edit_message_text("✅ Data sucessfully removed")

        # Llama a la función 'start' para mostrar los botones nuevamente
        keyboard = [
            [
                InlineKeyboardButton("Private Key", callback_data="button_1"),
                InlineKeyboardButton("Your Wallet", callback_data="button_2"),
            ],
            [
                InlineKeyboardButton("Token", callback_data="button_3"),
                InlineKeyboardButton("Target Wallet", callback_data="button_4"),
            ],
            [
                InlineKeyboardButton("Network", callback_data="button_5"),
                InlineKeyboardButton("To Network", callback_data="button_6"),
            ],
            [
                InlineKeyboardButton("Amount", callback_data="button_7"),
                InlineKeyboardButton("🗑 Clear Data", callback_data="clear_data"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("<b><u>🔗Steps to create a Bridge on BridgeHub:</u></b>\n\n 1.Enter your <b><u>private key</u></b> <i>(to sign both the bridge and approval contract)</i>\n 2.<b>Your wallet and destination wallet</b> are required.\n 3.You need to specify the <b>Token</b> <i>(available only USDC and ETH)</i>\n 4.Choose the starting and <b>destination blockchain network</b> (available ERC20 and BEP20 network)\n 5.Enter the <b>amount of ETH or USDC</b> you want to transfer through the bridge.\n\n<b><i>Note: You can clear the entered data by clicking '🗑Clear Data' </i></b>", reply_markup=reply_markup, parse_mode="html")


def message_handler(update: Update, context: CallbackContext):
    current_button = context.user_data.get("current_button")
    if current_button:
        context.user_data[current_button] = update.message.text
        context.user_data["current_button"] = None
        update.message.reply_text("Saved ✅")

        # Comprueba si todos los botones han sido seleccionados y se ha añadido un mensaje
        if all(key in context.user_data for key in ["button_1", "button_2", "button_3", "button_4", "button_5", "button_6", "button_7"]):
            summary = (
                f"<u>Here's your bride information:</u>\n"
                f"1. <b>Private key:</b>\n {context.user_data['button_1']}\n\n"
                f"2. <b>Wallet:</b>\n {context.user_data['button_2']}\n\n"
                f"3. <b>Token para hacer el bridge:</b>\n {context.user_data['button_3']}\n\n"
                f"4. <b>Destinatary wallet:</b>\n {context.user_data['button_4']}\n\n"
                f"5. <b>Your Network:</b>\n {context.user_data['button_5'].upper()}\n\n"
                f"6. <b>Destinatary Network:</b>\n {context.user_data['button_6'].upper()}\n\n"
                f"7. <b>{context.user_data['button_3'].upper()} Amount:</b>\n {context.user_data['button_7']}\n\n"
            )
            update.message.reply_text(summary, parse_mode="html")

            keyboard = [
                [InlineKeyboardButton("👍 Bridge now", callback_data="bridge")],
                [InlineKeyboardButton("❌ Cancel bridge", callback_data="cancel")],
                [InlineKeyboardButton("🗑 Clear Data", callback_data="clear_data")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("All options have been completed. What do you want to do?", reply_markup=reply_markup)
        else:
            # Actualiza los botones
            keyboard = [
                [
                    InlineKeyboardButton("✅Private Key" if "button_1" in context.user_data else "Private Key", callback_data="button_1"),
                    InlineKeyboardButton("✅Your Wallet" if "button_2" in context.user_data else "Your Wallet", callback_data="button_2"),
                ],
                [
                    InlineKeyboardButton("✅Token (USDC or ETH)" if "button_3" in context.user_data else "Token (USDC or ETH)", callback_data="button_3"),
                    InlineKeyboardButton("✅To Wallet" if "button_4" in context.user_data else "To Wallet", callback_data="button_4"),
                ],
                [
                    InlineKeyboardButton("✅Your Network" if "button_5" in context.user_data else "Your Network", callback_data="button_5"),
                    InlineKeyboardButton("✅To Network" if "button_6" in context.user_data else "To Network", callback_data="button_6"),
                ],
                [
                    InlineKeyboardButton("✅Amount" if "button_7" in context.user_data else "Amount", callback_data="button_7"),
                    InlineKeyboardButton("🗑 Clear Data", callback_data="clear_data")
                    
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("<b><u>🔗Steps to create a Bridge on BridgeHub:</u></b>\n\n 1.Enter your <b><u>private key</u></b> <i>(to sign both the bridge and approval contract)</i>\n 2.<b>Your wallet and destination wallet</b> are required.\n 3.You need to specify the <b>Token</b> <i>(available only USDC and ETH)</i>\n 4.Choose the starting and <b>destination blockchain network</b> (available ERC20 and BEP20 network)\n 5.Enter the <b>amount of ETH or USDC</b> you want to transfer through the bridge.\n\n<b><i>Note: You can clear the entered data by clicking '🗑Clear Data' </i></b>", reply_markup=reply_markup, parse_mode="html")

def bridge_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "bridge":
        # Aquí puedes llamar a la función para realizar el bridge
        query.answer(text="Haciendo el bridge...")
        chain_name = context.user_data['button_3'].upper()
        if chain_name == "USDC":
            #### USDC
            print(context.user_data['button_7'])
            amount = int(context.user_data['button_7'])
            integer_amount = decimal_to_integer(amount, chain_name)
            print("Amount:", integer_amount, f" Amount Formatted: ", integer_amount / (10 ** 6))
            # Get chain parameters
            TOKEN_CONTRACT_ADDRESS, TOKEN_ADDRESS, TOKEN_ABI, token_contract, token_contract_any = getTokenParameters(chain_name)

            # Configuración del contrato Router
            
            router_contract_address = w3.toChecksumAddress("0x6b7a87899490ece95443e979ca9485cbe7e71522")  # Ejemplo de dirección del contrato Router
            router_contract = w3.eth.contract(address=w3.toChecksumAddress(router_contract_address), abi=router_abi)

            nonce = w3.eth.get_transaction_count(w3.toChecksumAddress(context.user_data['button_2']), 'pending')
            # Aprobar el token (solo necesario la primera vez)
            approve = ensure_token_approval(integer_amount, token_contract, token_contract_any, chain_name, nonce, context.user_data['button_1'], context.user_data['button_5'], context, update,  w3.toChecksumAddress(context.user_data['button_2']), router_contract_address, router_contract)
            
            if approve:
                if context.user_data['button_6'].upper() == "BSC":
                    # Ejecutar la transacción de Anyswap
                    anyswap_out_underlying(w3.toChecksumAddress(context.user_data['button_4']), integer_amount, 56, token_contract, token_contract_any, w3.toChecksumAddress(context.user_data['button_2']), TOKEN_CONTRACT_ADDRESS, nonce, context.user_data['button_1'], context.user_data['button_5'], context, update, router_contract_address, router_contract)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="❌Fail.\nTry /start again")
        elif chain_name == "ETH":
            #### ETH
            context.user_data['button_7']
            amount = context.user_data['button_7']
            integer_amount = decimal_to_integer(amount, chain_name)
            print("Amount:", integer_amount, f" Amount Formatted: ", integer_amount / (10 ** 18))
            # Get chain parameters
            TOKEN_CONTRACT_ADDRESS, TOKEN_ADDRESS, TOKEN_ABI, token_contract, token_contract_any = getTokenParameters(chain_name)

            nonce = w3.eth.get_transaction_count(w3.toChecksumAddress(context.user_data['button_2']), 'pending')

            router_contract_address = w3.toChecksumAddress("0xBa8Da9dcF11B50B03fd5284f164Ef5cdEF910705")  # Ejemplo de dirección del contrato Router
            router_contract = w3.eth.contract(address=w3.toChecksumAddress(router_contract_address), abi=router_abi)

            # Aprobar el token (solo necesario la primera vez)
            approve = ensure_token_approval(integer_amount, token_contract, token_contract_any, chain_name, nonce, context.user_data['button_1'], context.user_data['button_5'], context, update,  w3.toChecksumAddress(context.user_data['button_2']), router_contract_address, router_contract)
            if approve:
                if context.user_data['button_6'].upper() == "BSC":
                    # Ejecutar la transacción de Anyswap
                    anyswap_out_underlying(w3.toChecksumAddress(context.user_data['button_4']), integer_amount, 56, token_contract, token_contract_any, w3.toChecksumAddress(context.user_data['button_2']), TOKEN_CONTRACT_ADDRESS, nonce, context.user_data['button_1'], context.user_data['button_5'], context, update, router_contract_address, router_contract)
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="❌Fail.\nTry /start again")
    elif query.data == "cancel":
        query.answer(text="❌Operation canceled")
    query.edit_message_text("Doing the Bridge Process...")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_callback, pattern="button_"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(CallbackQueryHandler(clear_data_callback, pattern="^clear_data$"))  # Asegúrate de agregar esta línea

    dp.add_handler(CallbackQueryHandler(bridge_callback, pattern="bridge|cancel"))

    updater.start_polling()
    updater.idle()

# ----------------------- #

# Configuración del token
def getTokenParameters(chain_name):
    if chain_name == "USDC":
        ### USDC
        TOKEN_CONTRACT_ADDRESS = w3.toChecksumAddress("0x7ea2be2df7ba6e54b1a9c70676f668455e329d29")
        TOKEN_ADDRESS = w3.toChecksumAddress("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48") 
        TOKEN_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_name","type":"string"},{"name":"_symbol","type":"string"},{"name":"_decimals","type":"uint8"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]')
        token_contract = w3.eth.contract(address=w3.toChecksumAddress(TOKEN_CONTRACT_ADDRESS), abi=TOKEN_ABI)
        token_contract_any = w3.eth.contract(address=w3.toChecksumAddress(TOKEN_ADDRESS), abi=TOKEN_ABI)
    elif chain_name == "ETH":
        ### WETH
        TOKEN_CONTRACT_ADDRESS = w3.toChecksumAddress("0x0615Dbba33Fe61a31c7eD131BDA6655Ed76748B1")
        TOKEN_ADDRESS = w3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        TOKEN_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]')
        token_contract = w3.eth.contract(address=w3.toChecksumAddress(TOKEN_CONTRACT_ADDRESS), abi=TOKEN_ABI)
        token_contract_any = w3.eth.contract(address=w3.toChecksumAddress(TOKEN_ADDRESS), abi=TOKEN_ABI)
    
    return TOKEN_CONTRACT_ADDRESS, TOKEN_ADDRESS, TOKEN_ABI, token_contract, token_contract_any

# Convert eth to decimals
def decimal_to_integer(number, chain_name):
    if chain_name == "ETH":
        # Convertir el número a una cadena para obtener la cantidad de decimales
        number_str = str(number)
        if '.' in number_str:
            decimals = len(number_str.split('.')[1])
        else:
            decimals = 0

        number_str = str(number).replace('.', '')
        integer_str = number_str.lstrip('0')
        integer_amount = int(integer_str)
        
        multiplier = 10 ** (18 - decimals)
        integer_amount = int(round(integer_amount * multiplier))

    elif chain_name == "USDC":
        multiplier = 10 ** 6
        integer_amount = number * (multiplier)
    return integer_amount

# Wait until the approve is done
def wait_for_receipt(tx_hash, retries=30, delay=10):
    for _ in range(retries):
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except TransactionNotFound:
            pass
        time.sleep(delay)
    raise Exception("Transaction not found after {} retries".format(retries))

# Aprobar el token subyacente para el contrato Router (solo necesario la primera vez)
def ensure_token_approval(amount, token_contract, token_contract_any, chain_name, nonce, private_key, network, context, update, your_wallet, router_contract_address, router_contract):
    allowance = token_contract_any.functions.allowance(your_wallet, router_contract_address).call()
    print(f"Allowance {chain_name}: {allowance}")
    
    allowance_anyusd = token_contract.functions.allowance(your_wallet, router_contract_address).call()
    print(f"Allowance any{chain_name}: {allowance_anyusd}")
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="🕐Approving token spend...")
    token_approval_tx = token_contract_any.functions.approve(router_contract_address, amount).build_transaction({
        'from': your_wallet,
        'gas': 150000,
        'nonce': nonce,
    })
    
    signed_tx = w3.eth.account.signTransaction(token_approval_tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    hash_url = ""

    if network.upper() == "ETH":
        hash_url = f"https://etherscan.io/tx/{tx_hash.hex()}"
        context.bot.send_message(chat_id=update.effective_chat.id, text= f"📋Token approval tx hash: \n{hash_url}")
        print(f"https://etherscan.io/tx/{tx_hash.hex()}")
    elif network.upper() == "BSC":
        hash_url = f"https://bscscan.com/tx/{tx_hash.hex()}"
        context.bot.send_message(chat_id=update.effective_chat.id, text= f"📋Token approval tx hash: \n{hash_url}")
        print(f"https://bscscan.com/tx/{tx_hash.hex()}")
    # Esperar a que se confirme la transacción de aprobación
    context.bot.send_message(chat_id=update.effective_chat.id, text= "🕐Waiting for token approval transaction confirmation...")
    time.sleep(5)
    wait_for_receipt(str(tx_hash.hex()))
    context.bot.send_message(chat_id=update.effective_chat.id, text= f"✅Token approval transaction confirmed.\n{hash_url}")
    return True
    
# Simulate the bridge before the transaction (to see if got an error)
def simulate_transaction(tx):
    try:
        result = w3.eth.call(tx)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

# Check Bridge Hash Transaction
def checkStatusTx(txHash):
    url = 'https://bridgeapi.anyswap.exchange/v2/history/details'

    response = requests.get(url, params={'params': txHash})

    print(response.text)

# Make the anyswap Bridge with the Router V6
def anyswap_out_underlying(to_address, amount, to_chain_id, token_contract, token_contract_any, your_wallet, TOKEN_CONTRACT_ADDRESS, nonce, private_key, network, context, update, router_contract_address, router_contract):
    allowance = token_contract.functions.allowance(your_wallet, router_contract_address).call()
    print(f"Allowance: {allowance}")
    balance = token_contract_any.functions.balanceOf(your_wallet).call()
    print(f"Balance: {balance}")

    estimated_gas = router_contract.functions.anySwapOutUnderlying(TOKEN_CONTRACT_ADDRESS, to_address, amount, to_chain_id).estimate_gas({'from': your_wallet}, block_identifier='latest')
    
    gas_with_margin = int(estimated_gas * 1.4)
    retry_counter = 0
    print(router_contract, TOKEN_CONTRACT_ADDRESS, to_address, token_contract_any, TOKEN_CONTRACT_ADDRESS)
    while retry_counter < 5:
        try:
            
            transaction_data = router_contract.functions.anySwapOutUnderlying(TOKEN_CONTRACT_ADDRESS, to_address, amount, to_chain_id).build_transaction({
                'from': your_wallet,
                'gas': gas_with_margin,
                'nonce': nonce,
            })

            simulation_result = simulate_transaction(transaction_data)
            if simulation_result is None:
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"📋Bridge from {network.upper()} tx hash: \n{hash_url}")

                print("The transaction would fail.")
                return
                
            signed_tx = w3.eth.account.signTransaction(transaction_data, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Anyswap out underlying tx hash: {tx_hash.hex()}")
            if network.upper() == "ETH":
                hash_url = f"https://etherscan.io/tx/{tx_hash.hex()}"
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"📋Bridge from {network.upper()} tx hash: \n{hash_url}")
                
            elif network.upper() == "BSC":
                hash_url = f"https://bscscan.com/tx/{tx_hash.hex()}"
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"📋Bridge from {network.upper()} tx hash: \n{hash_url}")

            checkStatusTx(str(tx_hash.hex()))
            context.bot.send_message(chat_id=update.effective_chat.id, text= f"The bridge will take between 2 and 10 minutes")

            break
        except ValueError as e:
            if 'nonce too low' in str(e):
                # Incrementa el nonce y reintenta la transacción
                nonce += 1
                retry_counter += 1
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"Retrying with a higher nonce ({nonce})...")

                time.sleep(2)  # Espera un poco antes de reintentar
            else:
                # Si el error es diferente, muestra el mensaje de error y sal del bucle
                context.bot.send_message(chat_id=update.effective_chat.id, text= f"Error while sending the transaction. {e}")

                print(f"Error al enviar la transacción: {e}")
                break

if __name__ == "__main__":
    main()
    