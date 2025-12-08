# def get_user_data_from_whatsapp_payload(body):
#     print("Received body:", body)
#     entry = body.get("entry", [])[0]
#     print("Entry:", entry)
#     changes = entry.get("changes", [])[0]
#     print("Changes:", changes)
    
#     value = changes.get("value", {})
#     print("Value:", value)
    
#     metadata = value.get("metadata", {})
#     print("metadata:", metadata)
    
#     contact = value.get("contacts", {})[0]
#     print("Contact:", contact)
    
#     name = contact["profile"]['name']
#     print("Name:", name)
    
#     wa_id = contact.get("wa_id")
#     print("WA ID:", wa_id)
    
#     display_phone_number = metadata.get('display_phone_number')
#     phone_number_id = metadata.get('phone_number_id')
    
#     print("===========")
#     print(display_phone_number)
#     print(phone_number_id)

#     return {
#         "name": name,
#         "phone": wa_id,
#         "display_phone_number": display_phone_number,
#         "phone_number_id": phone_number_id
#     }
    


def get_user_data_from_whatsapp_payload(body):
    print("Received body:", body)

    # --- SAFELY EXTRACT ENTRY ---
    entry = (body.get("entry") or [{}])[0]
    print("Entry:", entry)

    # --- SAFELY EXTRACT CHANGES ---
    changes = (entry.get("changes") or [{}])[0]
    print("Changes:", changes)

    # --- VALUE OBJECT ---
    value = changes.get("value", {}) or {}
    print("Value:", value)

    # --- METADATA ---
    metadata = value.get("metadata", {}) or {}
    print("metadata:", metadata)

    phone_number_id = metadata.get("phone_number_id")
    display_phone_number = metadata.get("display_phone_number")

    # -----------------------------------------------------
    # CASE 1: USER SENT A MESSAGE (contacts exists)
    # -----------------------------------------------------
    contacts = value.get("contacts")
    if contacts and isinstance(contacts, list) and len(contacts) > 0:
        contact = contacts[0]
        print("Contact:", contact)

        name = contact.get("profile", {}).get("name")
        wa_id = contact.get("wa_id")

        print("Name:", name)
        print("WA ID:", wa_id)
        print("============")

        return {
            "type": "message",
            "name": name,
            "phone": wa_id,
            "display_phone_number": display_phone_number,
            "phone_number_id": phone_number_id
        }

    # -----------------------------------------------------
    # CASE 2: MESSAGE STATUS UPDATE (NO contacts)
    # -----------------------------------------------------
    statuses = value.get("statuses")
    if statuses and isinstance(statuses, list) and len(statuses) > 0:
        status = statuses[0]
        wa_id = status.get("recipient_id")

        print("Status update for:", wa_id)
        print("============")

        return {
            "type": "status",
            "phone": wa_id,
            "display_phone_number": display_phone_number,
            "phone_number_id": phone_number_id
        }

    # -----------------------------------------------------
    # CASE 3: Unknown payload type (fallback)
    # -----------------------------------------------------
    print("Unknown payload shape. Returning metadata only.")
    print("============")

    return {
        "type": "unknown",
        "phone_number_id": phone_number_id,
        "display_phone_number": display_phone_number
    }
    
