dsl = """ENTITY USERS {

    LET ROOT = ROOT
    LET target = NEW

    LET source = $ROOT.data
    LET identity = $ROOT.source_identity
    POP source.category

    MOVE source.metadata -> target._meta.name
    MOVE source.characteristics -> target._meta.characteristics
    MOVE source.source[0].emails -> target._meta.emails
    MOVE identity -> target.identity
    FOREACH source.emails AS contact {

        MOVE contact.email_address -> target._meta.email

    }

    CONVERT TO_SNAKE_CASE(target)

}"""

