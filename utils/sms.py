from sms_ir import SmsIr
sms_ir = SmsIr("API")



def send_otp(phone,code):
    sms_ir.send_verify_code(
                number=phone,
                template_id=int("4324"),
                parameters=[
                        {
                            "name" : "CODE",
                            "value": str(code),
            
                        },
                        
                    ],
                )