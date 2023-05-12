from protofuzz import protofuzz

fuzzer = protofuzz.from_description_string("""
    import "google/protobuf/timestamp.proto";
    service eVoting {
        rpc PreAuth (VoterName) returns (Challenge);
        rpc Auth (AuthRequest) returns (AuthToken);
        rpc CreateElection (Election) returns (Status);
        rpc CastVote (Vote) returns (Status);
        rpc GetResult(ElectionName) returns (ElectionResult);
    }
    message Voter {
        required string name = 1;
        required string group = 2;
        required bytes public_key = 3;
    }
    message VoterName {
        required string name = 1;
    }
    message AuthRequest {
        required VoterName name = 1;
        required Response response = 2;
    }
    message Election {
        required string name = 1;
        required string groups = 2;
        required string choices = 3;
        required google.protobuf.Timestamp end_date = 4;
        required AuthToken token = 5;
    }
    message Vote {
        required string election_name = 1;
        required string choice_name = 2;
        required AuthToken token = 3;
    }
    message ElectionName {
        required string name = 1;
    }
    message Status {
        required int32 code = 1;
    }
    message Challenge {
        required bytes value = 1;
    }
    message AuthToken {
        required bytes value = 1;
    }
    message ElectionResult {
        required int32 status = 1;
        repeated VoteCount counts = 2;
    }
    message Response {
        required bytes value = 1;
    }
    message VoteCount {
        required string choice_name = 1;
        required int32 count = 2;
    }
""")

for obj in fuzzer['Voter'].permute():
    print("Generated object: {}".format(obj))

# 隨機生成 VoterName 對象
for obj in fuzzer['VoterName'].permute():
    print("Generated object: {}".format(obj))

# 隨機生成 AuthRequest 對象
for obj in fuzzer['AuthRequest'].permute():
    print("Generated object: {}".format(obj))

# 隨機生成 Election 對象
for obj in fuzzer['Election'].permute():
    print("Generated object: {}".format(obj))

# 隨機生成 Vote 對象
for obj in fuzzer['Vote'].permute():
    print("Generated object: {}".format(obj))

# 隨機生成 ElectionName 對象
for obj in fuzzer['ElectionName'].permute():
    print("Generated object: {}".format(obj))

for obj in fuzzer['Status'].permute():
    print("Generated object: {}".format(obj))

for obj in fuzzer['Challenge'].permute():
    print("Generated object: {}".format(obj))

for obj in fuzzer['AuthToken'].permute():
    print("Generated object: {}".format(obj))

for obj in fuzzer['ElectionResult'].permute():
    print("Generated object: {}".format(obj))

for obj in fuzzer['Response'].permute():
    print("Generated object: {}".format(obj))

for obj in fuzzer['VoteCount'].permute():
    print("Generated object: {}".format(obj))
