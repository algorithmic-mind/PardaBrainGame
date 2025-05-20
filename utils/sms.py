from sms_ir import SmsIr
sms_ir = SmsIr("7C59DyoSD7b9dnrMlxYPfo3CoKoTragY60luWMxEtScjEMZP")



def send_otp(phone,code):
    sms_ir.send_verify_code(
                number=phone,
                template_id=int("830439"),
                parameters=[
                        {
                            "name" : "CODE",
                            "value": str(code),
            
                        },
                        
                    ],
                )