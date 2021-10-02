""" from src.channels import channels_list_v1

def test_channels_list():
    assert channels_list_v1(1234) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            }
        ]

    }
    
     """

