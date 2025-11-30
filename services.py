def get_user_data_from_whatsapp_payload(body):
    print("Received body:", body)
    entry = body.get("entry", [])[0]
    print("Entry:", entry)
    changes = entry.get("changes", [])[0]
    print("Changes:", changes)
    value = changes.get("value", {})
    print("Value:", value)
    contact = value.get("contacts")[0]
    print("Contact:", contact)
    name = contact["profile"]['name']
    print("Name:", name)
    wa_id = contact.get("wa_id")
    print("WA ID:", wa_id)

    return {
        "name": name,
        "phone": wa_id
    }