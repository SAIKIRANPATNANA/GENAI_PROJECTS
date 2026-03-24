#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "comment.h"
#include "platform.h"
#include "post.h"
#include "reply.h"

reply* createReply(char* username, char* content, int n){
    reply* newReply = (reply*)malloc(sizeof(reply));
    // int num_lines;
    if(newReply!=NULL) {
        // char unformatted_username[25];
        // sscanf(username, "%[^_]_%d", unformatted_username, &num_lines);
        newReply->username = strdup(username);
        newReply->content = strdup(content);
        // newReply->content = (char**)malloc(sizeof(char*)*num_lines);
        // for(int i=0; i<num_lines; i++){
        //    newReply->content[i] = strdup(content[i]);
        // }
        newReply->nextReply = NULL;
        // newReply->num_lines = num_lines;
        if(pf->lastViewedPost->num_comments >= n){
            comment* tempComment = pf->lastViewedPost->comments;
            while(tempComment->nextComment!=NULL && tempComment->nextComment->id!=n){
                tempComment = tempComment->nextComment;
            }if(tempComment->nextComment!=NULL || pf->lastViewedPost->comments->id==n){
                if( pf->lastViewedPost->comments->id==n){
                    tempComment = pf->lastViewedPost->comments;
                }else{
                    tempComment = tempComment->nextComment;
                }if(tempComment->replies == NULL){
                    newReply->id = 1;
                    tempComment->replies = newReply;
                    tempComment->num_replies = 1;
                    return tempComment->replies;
                }reply* tempReply = tempComment->replies;
                while(tempReply->nextReply!=NULL){
                    tempReply = tempReply->nextReply;
                }newReply->id = tempReply->id+1;
                tempReply->nextReply = newReply;
                tempComment->num_replies += 1;
                return newReply;
            }
        }
    }return NULL;
}






