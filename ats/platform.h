typedef struct post post;  
typedef struct comment comment;
typedef struct reply reply;

typedef struct platform {
    struct post* posts;
    int num_posts;
    struct post* lastViewedPost;
}platform;

extern platform* pf;
extern int flag;

platform* createPlatform();
int addPost(char* username, char* caption);
void freeComments(comment* comments);
// void freeContent(char** content, int num_lines);
void freeComments(comment* replies);
int deletePost(int n);
post* viewPost(int n);
post* currPost();
post* nextPost();
post* previousPost();
int addComment(char* username , char* content);
int deleteComment(int n);
comment* viewComments();
int addReply(char* username , char* content, int n);
reply* viewReplies(int n);
int deleteReply(int n, int m);




