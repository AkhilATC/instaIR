dsl = """ENTITY USERS {

    LET ROOT = ROOT
    LET target = NEW

    LET source = $ROOT.data
    LET identity = $ROOT.source_identity
    POP source.security

    MOVE source.name -> target._meta.name
    MOVE source.characteristics -> target._meta

    FOREACH source.emails AS contact {

        MOVE contact.email_address -> target._meta.email

    }

    CONVERT TO_SNAKE_CASE(target)

}"""

