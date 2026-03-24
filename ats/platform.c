#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "platform.h"
#include "post.h"
#include "comment.h"
#include "reply.h"

platform* createPlatform() {
    platform* newPlatform = (platform*)malloc(sizeof(platform));
    if(newPlatform!=NULL && pf==NULL){
        newPlatform->num_posts = 0;
        newPlatform->lastViewedPost = NULL;
        newPlatform->posts = NULL;
        return newPlatform;
    }return NULL;
}int addPost(char* username, char* caption){
    post* newPost = createPost(username,caption);
    if(newPost!=NULL){
        if(pf->lastViewedPost==NULL){
            pf->lastViewedPost = newPost;
        }pf->num_posts += 1;
        return 1;
    }return 0;
}
void freeComments(comment* comments){
    while(comments!=NULL){
        comment* tempComment = comments;
        // freeContent(tempComment->content, tempComment->num_lines);
        free(tempComment->replies);
        free(tempComment->content);
        free(tempComment);
        comments = comments->nextComment;
    }return;
}void freeReplies(reply* replies){
    while(replies!=NULL){
        reply* tempReply = replies;
        free(tempReply->content);
        free(tempReply);
        replies = replies->nextReply;
    }return;
}
// void freeContent(char** content, int num_lines){
//     for(int i=0; i<num_lines; i++){
//         free(content[i]);
//     }free(content);
//     return;
// }
int deletePost(int n){
    if(n<=pf->num_posts){
        post* tempPost = pf->posts;
        if(n==1){
            pf->posts = tempPost->nextPost;
            // freeContent(tempPost->caption,tempPost->num_lines);
            free(tempPost->caption);
            freeComments(tempPost->comments);
            free(tempPost);
            return 1;
        }while(tempPost->nextPost!=NULL && tempPost->nextPost->id!=n){
            tempPost = tempPost->nextPost;
        }if(tempPost->nextPost!=NULL){
            post* delPost = tempPost->nextPost;
            tempPost->nextPost = tempPost->nextPost->nextPost;
            free(delPost->caption);
            freeComments(delPost->comments);
            free(delPost);
            return 1;
        }
    }return 0;
}post* viewPost(int n){
    if(n<=pf->num_posts){
        post* tempPost = pf->posts;
        while(tempPost!=NULL && tempPost->id!=n){
            tempPost = tempPost->nextPost;
        }if(tempPost!=NULL){
            pf->lastViewedPost = tempPost;
            flag = 0;
            return tempPost;
        }
    }return NULL;
}post* currPost(){
    if(pf->lastViewedPost!=NULL){
        if(flag && pf->num_posts>1 && pf->lastViewedPost==pf->posts){
            post* tempPost = pf->posts;
            while(tempPost->nextPost!=NULL){
                tempPost = tempPost->nextPost;
            }pf->lastViewedPost = tempPost;
        }return pf->lastViewedPost;
    }return NULL;
}post* nextPost(){
    if(pf->lastViewedPost!=NULL){
        if(pf->lastViewedPost->id ==  1){
            return pf->lastViewedPost;
        }else{
            int nextPost_id = pf->lastViewedPost->id-1;
            post* tempPost = pf->posts;
            while(tempPost!=NULL &&  tempPost->id!=nextPost_id){
                tempPost = tempPost->nextPost;
            }if(tempPost!=NULL){
                pf->lastViewedPost = tempPost;
                return tempPost;
            }
        }
    }return NULL;
}post* previousPost(){
    if(pf->lastViewedPost!=NULL &&  pf->num_posts>=pf->lastViewedPost->id){
        if(pf->num_posts == pf->lastViewedPost->id){
            return pf->lastViewedPost;
        }else{
            int previousPost_id = pf->lastViewedPost->id+1;
            post* tempPost = pf->posts;
            while(tempPost!=NULL &&  tempPost->id!=previousPost_id){
                tempPost = tempPost->nextPost;
            }if(tempPost!=NULL){
                pf->lastViewedPost = tempPost;
                return tempPost;
            }
        }
    }return NULL;
}int addComment(char* username , char* content){
    if(pf->lastViewedPost!=NULL){
       comment* newComment = createComment(username,content);
       if(newComment!=NULL){
           pf->lastViewedPost->num_comments += 1;
           return 1;
       }
    }return 0;
}int deleteComment(int n){
    if(pf->lastViewedPost!=NULL && pf->lastViewedPost->comments!=NULL && n<=pf->lastViewedPost->num_comments){
        comment* tempComment = pf->lastViewedPost->comments;
        if(tempComment->id == n){
            pf->lastViewedPost->comments = tempComment->nextComment;
            // freeContent(tempComment->content,tempComment->num_lines);
            free(tempComment->content);
            free(tempComment);
            return 1;
        }while(tempComment->nextComment!=NULL &&  tempComment->nextComment->id!=n){
            tempComment = tempComment->nextComment;
        }if(tempComment->nextComment!=NULL){
            comment* delComment = tempComment->nextComment;
            tempComment->nextComment = tempComment->nextComment->nextComment;
            free(delComment->content);
            free(delComment);
            return 1;
        }
    }return 0;
}comment* viewComments(){
    if(pf->lastViewedPost!=NULL &&  pf->lastViewedPost->comments!=NULL){
        return pf->lastViewedPost->comments;
    }return NULL;
}int addReply(char* username , char* content, int n){
    if(pf->lastViewedPost!=NULL && pf->lastViewedPost->comments!=NULL){
       reply* newReply = createReply(username,content,n);
       if(newReply!=NULL){
           return 1;
       }
    }return 0;
}reply* viewReplies(int n){
    if(pf->lastViewedPost!=NULL && pf->lastViewedPost->comments!=NULL && pf->lastViewedPost->comments->replies!=NULL){  
        if(n<=pf->lastViewedPost->num_comments){
            comment* tempComment = pf->lastViewedPost->comments;
            if(tempComment->id == n){
                return tempComment->replies;
            }else{
                while(tempComment!=NULL && tempComment->id != n){
                    tempComment = tempComment->nextComment;
                }if(tempComment!=NULL){
                    return tempComment->replies;
                }
            }
        }
    }return NULL;
}int deleteReply(int n, int m){
     if(pf->lastViewedPost!=NULL && pf->lastViewedPost->comments!=NULL && n<=pf->lastViewedPost->num_comments){
        comment* tempComment = pf->lastViewedPost->comments;
        if(n!=pf->lastViewedPost->comments->id){
            while(tempComment->nextComment!=NULL && tempComment->nextComment->id!=n){
                tempComment = tempComment->nextComment;
            }if(tempComment->nextComment!=NULL){
                tempComment = tempComment->nextComment;
            }else{
                return 0;
            }
        }if(tempComment->num_replies>=m && tempComment->replies!=NULL){
            reply* tempReply = tempComment->replies;
            if(m==tempComment->replies->id){
                tempComment->replies = tempComment->replies->nextReply;
                // freeContent(tempReply->content,tempReply->num_lines);
                free(tempReply->content);
                free(tempReply);
                return 1;
            }else {
                while(tempReply->nextReply!=NULL && tempReply->nextReply->id==m){
                    tempReply = tempReply->nextReply;
                }if(tempReply->nextReply!=NULL){
                    reply* delReply = tempReply->nextReply;
                    tempReply->nextReply = tempReply->nextReply->nextReply;
                    // freeContent(delReply->content,delReply->num_lines);
                    free(tempReply->content);
                    free(tempReply);
                    return 1;
                }
            }
        }
    }return 0;
}









