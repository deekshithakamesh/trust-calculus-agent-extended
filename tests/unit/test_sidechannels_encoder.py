from trustcalc.sidechannels import Decoder, Encoder


def test_sidechannel_encoder_exports_and_round_trips() -> None:
    encoder = Encoder()
    decoder = Decoder()

    secret = "hi"
    bits = encoder.encode(secret)

    assert bits == "0110100001101001"
    assert decoder.decode(bits) == secret
