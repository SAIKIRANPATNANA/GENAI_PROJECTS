#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "post.h"
#include "platform.h"
#include "comment.h"
#include "reply.h"

post* createPost(char* username, char* caption){
    post* newPost = (post*)malloc(sizeof(post));
    // int num_lines;
    if(newPost!=NULL){
        // char unformatted_username[25];
        // sscanf(username, "%[^_]_%d", unformatted_username, &num_lines);
        newPost->username = strdup(username);
        newPost->caption = strdup(caption);
        // newPost->caption = (char**)malloc(sizeof(char*)*num_lines);
        // for(int i=0; i<num_lines; i++){
        //    newPost->caption[i] = strdup(caption[i]);
        // }
        newPost->num_comments = 0;
        // newPost->num_lines = num_lines;
        newPost->nextPost = NULL;
        newPost->comments = NULL;
        if(pf->posts==NULL) {
            newPost->id = 1;
            pf->posts = newPost;
            return pf->posts;
        }post* tempPost = pf->posts;
        while(tempPost->nextPost!=NULL){
            tempPost = tempPost->nextPost;
        }newPost->id = tempPost->id+1;
        tempPost->nextPost = newPost;
        return newPost;
    }return NULL;
}

















