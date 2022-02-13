from os import access
from scripts.general_scripts import get_account, get_contract
from brownie import config, network, DappToken, TokenFarm


KEPT_BALANCE = 1_000 * (10**18)


def main():
    deploy_token_farm_and_dapp_token()

def deploy_token_farm_and_dapp_token():
    account = get_account()
    dapp_token = DappToken.deploy({'from':account}, publish_source=config['networks'][network.show_active()]['verify'])
    token_farm = TokenFarm.deploy(dapp_token.address, {'from':account}, publish_source=config['networks'][network.show_active()]['verify'])

    tx = dapp_token.transfer(token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {'from':account})
    tx.wait(1)

    weth_token = get_contract('weth_token')
    fau_token = get_contract('fau_token')
    allowed_tokens = {
        dapp_token: get_contract('dai_usd_price_feed'),
        fau_token: get_contract('dai_usd_price_feed'),
        weth_token: get_contract('eth_usd_price_feed')
    }
    add_allowed_tokens(token_farm, allowed_tokens, account)

    return token_farm, dapp_token
    
def add_allowed_tokens(token_farm, allowed_tokens, account):
    for token in allowed_tokens:
        token_farm.addAllowedTokens(token.address, {'from':account}).wait(1)
        token_farm.setPriceFeedContract(token.address, allowed_tokens[token], {'from':account}).wait(1)
    
    return token_farm
