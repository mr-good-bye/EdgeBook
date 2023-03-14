module default {
    scalar type vape_puff_id extending sequence;
    scalar type fuel_entry_id extending sequence;
    scalar type oil_entry_id extending sequence;

    type VapePuff {
        required property num -> vape_puff_id;
        required property puffs -> int32;
        required property date -> cal::local_datetime;
    }

    type FuelEntry {
        required property num -> fuel_entry_id;
        required property mileage -> int64;
        required property fuel -> float32;
        required property date -> cal::local_date;
    }

    type OilEntry {
        required property num -> oil_entry_id;
        required property mileage -> int64;
        required property date -> cal::local_date;
        required property oil -> float32;
        required property oil_level -> float32{
            constraint min_value(0.0);
            constraint max_value(1.0);
        };
    }

    type User {
        required property username -> str{
            constraint exclusive;
            constraint min_len_value(3);
            constraint max_len_value(30);
        };
        property hash -> str;
    }

    type Token {
        required property token -> str{
            constraint exclusive;
        };
        required link user -> User;
        required property created -> std::datetime;
    }

    type NonUser {
        required property username -> str{
            constraint exclusive;
            constraint min_len_value(3);
            constraint max_len_value(30);
        };
        property hash -> str;
        property created -> std::datetime{
            default := datetime_current();
        }
    }
};
