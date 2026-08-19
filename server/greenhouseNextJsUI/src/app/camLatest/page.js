'use client';

import React, { useState, useEffect } from 'react';
import { Grid, Loading, Column } from '@carbon/react';
const config = require('../config/config.js');
const endpoints = require('../config/endpoints.js');

function CamPage(id) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState();
  const [latestCam1, setlatestCam1] = useState(null);
  const [latestCam2, setlatestCam2] = useState(null);
  const [latestCam3, setlatestCam3] = useState(null);
  const [latestCam4, setlatestCam4] = useState(null);


  const setEnv = async (event) => {
    console.log('Event: ' + JSON.stringify(event));
    config.setEnv(event);
    setLoading(true);
    setlatestCam1(null);
    await getlatestCam(1, setlatestCam1);
    setlatestCam2(null);
    await getlatestCam(2, setlatestCam2);
    setlatestCam3(null);
    await getlatestCam(3, setlatestCam3);
    setlatestCam4(null);
    await getlatestCam(4, setlatestCam4);
    setLoading(false);
  };

  const renderPhoto = (photos) => {
    const image = photos && photos.length > 0 ? photos[0] : null;
    if (!image) return null;

    return (
      <img
        src={'data:image/jpeg;base64,' + image.photo}
        alt={image.timestamp || 'Camera image'}
        style={{
          width: '100%',
          display: 'block',
          height: 'auto',
          maxHeight: '500px',
          objectFit: 'contain',
          borderRadius: '4px',
        }}
      />
    );
  };

  const getlatestCam = async (id, setImages) => {
    const ONE_SECOND = 1000;
    await new Promise((resolve) => setTimeout(resolve, ONE_SECOND));

    console.log('**CAM ID: ' + id);

    const camEndpoint =
      endpoints.getEndpoint() + endpoints.latestPhotoService + '?camId=cam' + id;

    await fetch(camEndpoint, {
      method: 'get',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (response.status == 200) {
          response.json().then((camData) => {
            setImages(camData.Docs);
          }, []);
        }
      })
      .catch((err) => {
        console.log(err);
        return <Grid className="cam-page">Loading</Grid>;
      });

    setLoading(false);
  };

  useEffect(() => {
    const refreshCameras = async () => {
      setLoading(true);
      setlatestCam1(null);
      setlatestCam2(null);
      setlatestCam3(null);
      setlatestCam4(null);

      await getlatestCam(1, setlatestCam1);
      await getlatestCam(2, setlatestCam2);
      await getlatestCam(3, setlatestCam3);
      await getlatestCam(4, setlatestCam4);
      setLoading(false);
    };

    refreshCameras();

    const intervalId = setInterval(() => {
      refreshCameras();
    }, 600000);  // Refresh every 10 minutes

    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return <Loading active className="cam-class" description="Loading" />;
  }

  if (error) {
    return `Error! ${error}`;
  }

  return (
    <Grid
      className="landing-page"
      fullWidth
      style={{
        margin: 0,
        padding: 0,
        width: '100vw',
        maxWidth: '100vw',
        marginLeft: '-1rem',
        marginRight: '-1rem',
        rowGap: 0,
        columnGap: 0,
      }}>
      <Column
        lg={8}
        md={4}
        sm={2}
        className="landing-page__content"
        style={{ padding: 0, margin: 0, height: 'auto', lineHeight: 0 }}>
        {renderPhoto(latestCam1)}
      </Column>

      <Column
        lg={8}
        md={4}
        sm={2}
        className="landing-page__content"
        style={{ padding: 0, margin: 0, height: 'auto', lineHeight: 0 }}>
        {renderPhoto(latestCam2)}
      </Column>

      <Column
        lg={8}
        md={4}
        sm={2}
        className="landing-page__content"
        style={{ padding: 0, margin: 0, height: 'auto', lineHeight: 0 }}>
        {renderPhoto(latestCam3)}
      </Column>

      <Column
        lg={8}
        md={4}
        sm={2}
        className="landing-page__content"
        style={{ padding: 0, margin: 0, height: 'auto', lineHeight: 0 }}>
        {renderPhoto(latestCam4)}
      </Column>
    </Grid>
  );
}
export default CamPage;
