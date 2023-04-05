cd ./webui
bash build.sh
cd ..

cd ./orchestrator
bash build.sh
cd ..

cd ./cli
bash build.sh
cd ..

cd ./input_modules/DICOM
bash build.sh
cd ../..

cd ./input_modules/HL7
bash build.sh
cd ../..

cd ./input_modules/HTTP
bash build.sh
cd ../..


cd ./input_modules/IOStream
bash build.sh
cd ../..


cd ./output_modules/DICOM
bash build.sh
cd ../..

cd ./output_modules/HL7
bash build.sh
cd ../..

cd ./output_modules/HTTP
bash build.sh
cd ../..


cd ./output_modules/IOStream
bash build.sh
cd ../..