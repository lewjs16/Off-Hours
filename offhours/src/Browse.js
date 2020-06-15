import React from 'react'
import styled from 'styled-components';

const Styles = styled.div`
 .subject {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 20px 20px;
    grid-template-columns: auto auto auto auto auto;
    justify-content: start;
  }
  .avatar {
      border-radius : %50;
      width: 50px;
      height: 50px;
  }
`;

const Browse = () => {
    let subjects = [];

    subjects = [
        {
            subject: "AP Chemistry",
            streams: [
                {
                    streamer : "Raul Dutta",
                    streamerImg : "./img/userImg/userimg1.png",
                    streamImg : "/img/streamImg/stream1.jpg",
                    streamId : "/watch/0",
                },
                {
                    streamer : "Daniel Zheng",
                    streamerImg : "./img/userImg/userimg2.jpg",
                    streamImg : "/img/streamImg/stream2.jpg",
                    streamId : "/watch/1",
                },
                {
                    streamer : "Jillian Lew",
                    streamerImg : "./img/userImg/userimg2.jpg",
                    streamImg : "/img/streamImg/stream3.jpg",
                    streamId : "/watch/3",
                }
            ]
        },
        {
            subject: "EECS 281",
            streams: [
                {
                    streamer : "Jillian Lew",
                    streamerImg : "./img/userImg/userimg2.jpg",
                    streamImg : "/img/streamImg/stream4.jpg",
                    streamId : "/watch/2",
                }
            ]
        },
    ]
    

    return(
        <Styles>
            {subjects.map((subject) => 
                <div>
                    {subject['subject']}

                    <div class="subject">
                        {subject['streams'].map((stream)=>
                            <div>
                                <img src={require(stream['streamerImg'])}></img>
                                {stream['streamer']}
                            </div>
                        )}
                    </div>

                </div>)}
        </Styles>
    )
}

export default Browse;