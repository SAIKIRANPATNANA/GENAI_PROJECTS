typedef struct platform platform;
typedef struct post post;
typedef struct comment comment;

typedef struct reply{
    int id;
    char* username;
    char* content;
    struct reply* nextReply;
    // int num_lines;
}reply;

reply* createReply(char* username, char* content, int n);


