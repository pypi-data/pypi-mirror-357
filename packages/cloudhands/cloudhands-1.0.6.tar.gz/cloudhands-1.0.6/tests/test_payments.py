import os
from src.cloudhands import CloudHandsPayment
from dotenv import load_dotenv
from src.cloudhands.sdk_types import ChargeType

load_dotenv()
author_key = os.getenv("AUTHOR_KEY")
chPay = CloudHandsPayment(
    author_key=author_key,
)

def test_simple_charge():
    """
    Test a simple charge using the CloudHandsPayment SDK.
    """ 
    # Charge usage.
    result = chPay.charge(
        charge=0,
        event_name="PYTHON SDK DEMO",
    )

    print("Charge result:", result.__dict__)
    if result.is_successful:
        print("Usage event posted successfully!")
        print("getting transaction for transaction_id:", result.transaction_id)
        transaction = chPay.get_transaction(result.transaction_id)
        print("Transaction details:", transaction.__dict__)
    else:
        print("Failed to post usage event.")
        if result.errors:
            print("Errors:", result.errors)

def test_variable_charge():
    """
    Test a variable charge using the CloudHandsPayment SDK.
    """
    # Variable charge usage.
    result = chPay.charge(
        charge=1,
        event_name="PYTHON SDK DEMO",
        charge_type=ChargeType.Variable,
    )

    print("Charge result:", result.__dict__)
    if result.is_successful:
        print("Usage event posted successfully!")
        # Complete the transaction for 0 credits 
        res = chPay.complete_cloudhands_transaction(
            transaction_id=result.transaction_id,
            charge=0,
        )
        print("Complete transaction result:", res.__dict__)
        print("getting transaction for transaction_id:", res.transaction_id)
        transaction = chPay.get_transaction(res.transaction_id)
        print("Transaction details:", transaction.__dict__)
    else:
        print("Failed to post usage event.")
        if result.errors:
            print("Errors:", result.errors)

def main():
    chPay.cli_authorize()

    print("CloudHands SDK initialized.")
    print("SDK values:", chPay.__dict__ )
    # Charge usage.
    print("Testing simple charge...")
    test_simple_charge()
    print("Testing variable charge...")
    test_variable_charge()

if __name__ == "__main__":
    main()

