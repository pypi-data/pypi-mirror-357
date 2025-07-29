from chuangsiai_sdk import ChuangsiaiClient

def main():
    # client = ChuangsiaiClient(api_key="apikey_d998e03048a696a41c676384d2a0a5b6")
    client = ChuangsiaiClient(access_key="ak_ca4ce56dd31af6b53aecae0bc5a83e75",secret_key="sk_261e277d782191ac31c798c5a1737ba1a10b854898125e441a33158782c4ea27")
    
    resp =  client.input_guardrail(strategy_key="669358997282885", content="测试内容")
    resp2 =  client.output_guardrail(strategy_key="669358997282885", content="测试内容")

    print(resp)
    print("/n/n")
    print(resp2)

if __name__ == "__main__":
    main()