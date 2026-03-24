typedef struct platform platform;
typedef struct post post;
typedef struct reply reply;

typedef struct comment{
    int id;
    char* username;
    char* content;
    struct comment* nextComment;
    struct reply* replies;
    // int num_lines;
    int num_replies;
}comment;

comment* createComment(char* username, char* content);


